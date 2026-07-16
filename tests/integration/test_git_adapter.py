"""Integration tests for the Git adapter against real temporary repositories."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from workattest.adapters.git import GitAdapter, GitError
from workattest.adapters.git.flow import build_change_receipt
from workattest.crypto.keys import KeyPair
from workattest.domain.enums import Decision, RiskClass
from workattest.hashing import hash_bytes
from workattest.receipts.verifier import verify_receipt
from workattest.verification import Check


def _keys():
    return dict(issuer_key=KeyPair.generate(), agent_key=KeyPair.generate())

NOW = "2026-01-01T00:00:00Z"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=str(repo), check=True, capture_output=True)


def _write(repo: Path, rel: str, content: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8", newline="\n")


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    _git(tmp_path, "config", "core.autocrlf", "false")
    _write(tmp_path, "src/app.py", "print('v1')\n")
    _write(tmp_path, "src/old.py", "old\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-m", "initial")
    return tmp_path


def test_rejects_non_repo(tmp_path: Path):
    with pytest.raises(GitError):
        GitAdapter(tmp_path / "not-a-repo")


def test_snapshot_reads_head_and_clean(repo: Path):
    snap = GitAdapter(repo).snapshot(NOW)
    assert snap.commit and len(snap.commit) == 40
    assert snap.clean is True


def test_collect_worktree_add_modify_delete(repo: Path):
    _write(repo, "src/app.py", "print('v2')\n")   # modify
    _write(repo, "src/new.py", "new\n")            # add (untracked)
    (repo / "src/old.py").unlink()                 # delete
    arts = {a.path_or_uri: a for a in GitAdapter(repo).collect_artifacts("HEAD")}

    assert set(arts) == {"src/app.py", "src/new.py", "src/old.py"}
    # modified: both hashes present and different
    assert arts["src/app.py"].before_hash is not None
    assert arts["src/app.py"].after_hash is not None
    assert arts["src/app.py"].before_hash != arts["src/app.py"].after_hash
    # added: no before, has after
    assert arts["src/new.py"].before_hash is None
    assert arts["src/new.py"].after_hash is not None
    # deleted: has before, no after
    assert arts["src/old.py"].before_hash is not None
    assert arts["src/old.py"].after_hash is None


def test_blob_hash_matches_disk_bytes(repo: Path):
    _write(repo, "src/app.py", "print('v2')\n")
    adapter = GitAdapter(repo)
    expected = hash_bytes((repo / "src/app.py").read_bytes())
    assert adapter.blob_hash(None, "src/app.py") == expected  # None => working tree


def test_diff_hash_is_deterministic(repo: Path):
    _write(repo, "src/app.py", "print('v2')\n")
    adapter = GitAdapter(repo)
    assert adapter.diff_hash("HEAD") == adapter.diff_hash("HEAD")


def test_receipt_accept_for_in_scope_commit(repo: Path):
    _write(repo, "src/app.py", "print('v2')\n")
    _git(repo, "commit", "-am", "fix in scope")
    result = build_change_receipt(
        repo_path=str(repo), before_ref="HEAD~1", after_ref="HEAD",
        allowed_prefix="src/", issuer_key=KeyPair.generate(), agent_key=KeyPair.generate(), now=NOW,
    )
    assert result.decision is Decision.ACCEPT
    assert verify_receipt(result.receipt).valid


def test_receipt_refuse_for_out_of_scope_change(repo: Path):
    _write(repo, "config/secrets.env", "TOKEN=abc\n")  # outside src/
    _git(repo, "add", "-A")
    _git(repo, "commit", "-am", "touch out of scope")
    result = build_change_receipt(
        repo_path=str(repo), before_ref="HEAD~1", after_ref="HEAD",
        allowed_prefix="src/", issuer_key=KeyPair.generate(), agent_key=KeyPair.generate(), now=NOW,
    )
    assert result.decision is Decision.REFUSE
    assert any("outside the authorized scope" in r for r in result.reasons)
    # A REFUSE receipt is still a valid, signed, verifiable record of the refusal.
    assert verify_receipt(result.receipt).valid


def test_receipt_hold_when_high_risk_without_approval(repo: Path):
    _write(repo, "src/app.py", "print('v2')\n")
    _git(repo, "commit", "-am", "risky change")
    result = build_change_receipt(
        repo_path=str(repo), before_ref="HEAD~1", after_ref="HEAD",
        allowed_prefix="src/", issuer_key=KeyPair.generate(), agent_key=KeyPair.generate(),
        now=NOW, risk=RiskClass.HIGH,
    )
    assert result.decision is Decision.HOLD  # INV-16


def test_high_risk_accepts_with_signed_approval(repo: Path):  # INV-10 / INV-16
    _write(repo, "src/app.py", "print('v2')\n")
    _git(repo, "commit", "-am", "risky but approved")
    result = build_change_receipt(
        repo_path=str(repo), before_ref="HEAD~1", after_ref="HEAD",
        allowed_prefix="src/", now=NOW, risk=RiskClass.HIGH,
        approver_key=KeyPair.generate(), **_keys(),
    )
    assert result.decision is Decision.ACCEPT
    report = verify_receipt(result.receipt)
    assert report.valid, report.summary()
    # the approval-signature check ran and passed
    assert any("approval signatures valid" in name and ok for name, ok, _ in report.checks)


def test_receipt_accept_with_passing_mandatory_check(repo: Path):
    _write(repo, "src/app.py", "print('v2')\n")
    _git(repo, "commit", "-am", "fix")
    checks = [Check(id="tests", command=(sys.executable, "-c", "import sys; sys.exit(0)"), mandatory=True)]
    result = build_change_receipt(
        repo_path=str(repo), before_ref="HEAD~1", after_ref="HEAD",
        allowed_prefix="src/", now=NOW, checks=checks, **_keys(),
    )
    assert result.decision is Decision.ACCEPT
    assert verify_receipt(result.receipt).valid
    vr = result.receipt["verification"]
    assert len(vr) == 1 and vr[0]["status"] == "passed"


def test_receipt_hold_with_failing_mandatory_check(repo: Path):  # INV-8
    _write(repo, "src/app.py", "print('v2')\n")
    _git(repo, "commit", "-am", "fix")
    checks = [Check(id="tests", command=(sys.executable, "-c", "import sys; sys.exit(1)"), mandatory=True)]
    result = build_change_receipt(
        repo_path=str(repo), before_ref="HEAD~1", after_ref="HEAD",
        allowed_prefix="src/", now=NOW, checks=checks, **_keys(),
    )
    assert result.decision is Decision.HOLD
    assert any("mandatory check 'tests'" in r for r in result.reasons)
    # A HOLD receipt is still a valid, signed record.
    assert verify_receipt(result.receipt).valid
