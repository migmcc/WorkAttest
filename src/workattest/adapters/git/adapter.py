"""Observe a Git repository and turn a change into verifiable evidence.

The adapter shells out to ``git`` and reads facts from the repository itself: the commit
before and after, which files changed, and the content hash of each file at each ref. It
does not rely on anything the agent claims (INV-4). File blobs are hashed with SHA-256
over their raw bytes; the resulting :class:`~workattest.hashing.HashRef`s populate
``ArtifactEvidence.before_hash`` / ``after_hash`` (INV-6).

``after_ref=None`` compares a ref (e.g. ``HEAD``) against the current working tree, so an
uncommitted AI-produced change can be captured before it is committed.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from ...domain.entities import ArtifactEvidence
from ...hashing import HashRef, hash_bytes
from ...ids import new_id

WORKTREE = None  # sentinel meaning "the current working tree"


class GitError(RuntimeError):
    """A git invocation failed."""


@dataclass(frozen=True)
class GitSnapshot:
    """A point-in-time observation of the repository."""

    commit: Optional[str]
    branch: Optional[str]
    tree_hash: Optional[str]
    clean: bool
    observed_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "commit": self.commit,
            "branch": self.branch,
            "tree_hash": self.tree_hash,
            "clean": self.clean,
            "observed_at": self.observed_at,
        }


class GitAdapter:
    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        if not (self.repo_path / ".git").exists():
            raise GitError(f"not a git repository: {self.repo_path}")

    # --- low-level ---------------------------------------------------------
    def _run(self, *args: str, allow_fail: bool = False) -> subprocess.CompletedProcess:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(self.repo_path),
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0 and not allow_fail:
            raise GitError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
        return proc

    def _run_bytes(self, *args: str, allow_fail: bool = False) -> Optional[bytes]:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(self.repo_path),
            capture_output=True,
        )
        if proc.returncode != 0:
            if allow_fail:
                return None
            raise GitError(f"git {' '.join(args)} failed: {proc.stderr.decode(errors='replace').strip()}")
        return proc.stdout

    # --- observations ------------------------------------------------------
    def head_commit(self) -> Optional[str]:
        proc = self._run("rev-parse", "HEAD", allow_fail=True)
        return proc.stdout.strip() if proc.returncode == 0 else None

    def current_branch(self) -> Optional[str]:
        proc = self._run("rev-parse", "--abbrev-ref", "HEAD", allow_fail=True)
        branch = proc.stdout.strip() if proc.returncode == 0 else None
        return branch or None

    def tree_hash(self, ref: str = "HEAD") -> Optional[str]:
        proc = self._run("rev-parse", f"{ref}^{{tree}}", allow_fail=True)
        return proc.stdout.strip() if proc.returncode == 0 else None

    def is_clean(self) -> bool:
        return self._run("status", "--porcelain").stdout.strip() == ""

    def snapshot(self, observed_at: str) -> GitSnapshot:
        return GitSnapshot(
            commit=self.head_commit(),
            branch=self.current_branch(),
            tree_hash=self.tree_hash(),
            clean=self.is_clean(),
            observed_at=observed_at,
        )

    def blob_hash(self, ref: Optional[str], path: str) -> Optional[HashRef]:
        """SHA-256 of ``path``'s content at ``ref`` (or the working tree if ref is None).

        Returns ``None`` when the file does not exist at that ref (added/deleted).
        """
        if ref is WORKTREE:
            full = self.repo_path / path
            if not full.is_file():
                return None
            return hash_bytes(full.read_bytes())
        content = self._run_bytes("show", f"{ref}:{path}", allow_fail=True)
        if content is None:
            return None
        return hash_bytes(content)

    def _worktree_paths(self) -> list[str]:
        """All paths differing between HEAD and the working tree, incl. untracked files."""
        out = self._run("status", "--porcelain").stdout
        paths: set[str] = set()
        for line in out.splitlines():
            if len(line) < 4:
                continue
            entry = line[3:]  # strip the two status columns + separating space
            if " -> " in entry:  # rename/copy: take the destination
                entry = entry.split(" -> ", 1)[1]
            paths.add(entry.strip().strip('"'))
        return sorted(paths)

    def changed_paths(self, before_ref: str, after_ref: Optional[str] = WORKTREE) -> list[str]:
        """Paths changed between two refs (or ref → working tree).

        Working-tree comparison uses ``git status`` so untracked new files are included
        (``git diff`` alone would miss them). Statuses are derived downstream from the
        presence of before/after content hashes, not from git's status letters.
        """
        if after_ref is WORKTREE:
            return self._worktree_paths()
        out = self._run("diff", "--name-only", before_ref, after_ref).stdout
        return sorted({ln.strip() for ln in out.splitlines() if ln.strip()})

    def diff_text(self, before_ref: str, after_ref: Optional[str] = WORKTREE) -> str:
        args = ["diff", before_ref]
        if after_ref is not WORKTREE:
            args.append(after_ref)  # type: ignore[arg-type]
        return self._run(*args).stdout

    def collect_artifacts(
        self, before_ref: str, after_ref: Optional[str] = WORKTREE
    ) -> list[ArtifactEvidence]:
        """Build ArtifactEvidence for every changed file, with before/after hashes.

        The add/modify/delete status is implied by which hashes are present: no
        before → added, no after → deleted, both → modified (INV-6).
        """
        artifacts: list[ArtifactEvidence] = []
        for path in self.changed_paths(before_ref, after_ref):
            before = self.blob_hash(before_ref, path)
            after = self.blob_hash(after_ref, path)
            if before is None and after is None:
                continue  # e.g. an ignored/transient path with no content either side
            size = None
            if after is not None and after_ref is WORKTREE:
                full = self.repo_path / path
                if full.is_file():
                    size = full.stat().st_size
            artifacts.append(
                ArtifactEvidence(
                    id=new_id("art"),
                    path_or_uri=path,
                    source="git",
                    before_hash=before,
                    after_hash=after,
                    size=size,
                )
            )
        return artifacts

    def diff_hash(self, before_ref: str, after_ref: Optional[str] = WORKTREE) -> HashRef:
        """Hash of the unified diff text — a compact fingerprint of the change."""
        return hash_bytes(self.diff_text(before_ref, after_ref).encode("utf-8"))
