"""Execute operator-defined checks and produce attested VerificationResults.

Security note: a check runs an arbitrary command, so check definitions are **trusted
operator input** — never anything the agent under evaluation can choose or modify
(INV-5). See SECURITY.md. Each run is bounded by a timeout to prevent hangs.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Sequence

from ..domain.entities import VerificationResult
from ..domain.enums import VerificationStatus
from ..hashing import HashRef, hash_bytes, hash_canonical
from ..ids import new_id

DEFAULT_TIMEOUT_S = 300


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class Check:
    """An operator-defined verification check."""

    id: str
    command: tuple[str, ...]
    name: Optional[str] = None
    version: str = "1.0"
    mandatory: bool = False
    tool: Optional[str] = None
    timeout_s: int = DEFAULT_TIMEOUT_S

    def definition(self) -> dict[str, Any]:
        """Canonical, hashable definition of the check (INV-7)."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "command": list(self.command),
            "mandatory": self.mandatory,
            "tool": self.tool,
        }

    def definition_hash(self) -> HashRef:
        return hash_canonical(self.definition())


def run_check(check: Check, cwd: str | Path) -> VerificationResult:
    """Run one check as a subprocess and attest the result.

    ``passed`` iff exit code 0; a non-zero exit is ``failed``; a timeout or launch
    failure is ``error``. The combined stdout+stderr is hashed (not stored inline) so the
    output is attestable without leaking potentially sensitive content (INV-19).
    """
    started = _now()
    status = VerificationStatus.PASSED
    exit_code: Optional[int] = None
    output = b""
    try:
        proc = subprocess.run(
            list(check.command),
            cwd=str(cwd),
            capture_output=True,
            timeout=check.timeout_s,
        )
        exit_code = proc.returncode
        output = (proc.stdout or b"") + (proc.stderr or b"")
        status = VerificationStatus.PASSED if exit_code == 0 else VerificationStatus.FAILED
    except subprocess.TimeoutExpired:
        status = VerificationStatus.ERROR
        output = b"timeout"
    except (OSError, ValueError) as exc:
        status = VerificationStatus.ERROR
        output = f"launch error: {exc}".encode()

    return VerificationResult(
        id=new_id("vr"),
        check_id=check.id,
        name=check.name,
        check_version=check.version,
        definition_hash=check.definition_hash(),
        status=status,
        tool=check.tool,
        command=" ".join(check.command),
        mandatory=check.mandatory,
        started_at=started,
        ended_at=_now(),
        exit_code=exit_code,
        output_hash=hash_bytes(output),
    )


def run_checks(checks: Sequence[Check], cwd: str | Path) -> list[VerificationResult]:
    """Run all checks in order and return their attested results."""
    return [run_check(c, cwd) for c in checks]


def load_checks(path: str | Path) -> list[Check]:
    """Load an operator check config (JSON list of check objects).

    Each entry: ``{"id", "command": [...], "name"?, "version"?, "mandatory"?, "tool"?,
    "timeout_s"?}``. This file is trusted operator input (INV-5).
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("checks config must be a JSON list")
    checks: list[Check] = []
    for entry in data:
        if "command" not in entry or not isinstance(entry["command"], list):
            raise ValueError(f"check {entry.get('id')!r} needs a 'command' list")
        checks.append(
            Check(
                id=entry["id"],
                command=tuple(str(x) for x in entry["command"]),
                name=entry.get("name"),
                version=str(entry.get("version", "1.0")),
                mandatory=bool(entry.get("mandatory", False)),
                tool=entry.get("tool"),
                timeout_s=int(entry.get("timeout_s", DEFAULT_TIMEOUT_S)),
            )
        )
    return checks
