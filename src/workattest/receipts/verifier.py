"""Offline receipt verifier.

Validates a receipt using only its own contents plus the public keys embedded in its
signatures — no server, no network (INV-15). Returns a structured report so callers can
see exactly which checks passed or failed.

Checks performed:
- schema version is supported;
- receipt_hash matches the recomputed payload hash (INV-14, T-1);
- at least one signature is valid over the payload (INV-13);
- every approval binds to THIS execution and to the receipt's result hash
  (INV-9, cross-execution guard, T-6);
- if the decision is ACCEPT, required structural elements are present.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .. import RECEIPT_SCHEMA_VERSION
from ..approval import verify_approval_signature
from ..canonical import canonical_bytes
from ..crypto.signing import Signature, verify
from ..hashing import HashRef, hash_bytes, hash_canonical
from ..redaction import verify_commitment

_UNCOVERED = ("signatures", "receipt_hash", "disclosures")


def _payload(receipt: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in receipt.items() if k not in _UNCOVERED}


def _expected_result_hash(receipt: dict[str, Any]) -> dict[str, str]:
    material = {
        "execution": receipt.get("execution"),
        "artifacts": receipt.get("artifacts", []),
        "verification": receipt.get("verification", []),
        "actions_root": receipt.get("actions_root"),
    }
    return hash_canonical(material).to_dict()


@dataclass
class VerificationReport:
    valid: bool = True
    checks: list[tuple[str, bool, str]] = field(default_factory=list)

    def record(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append((name, ok, detail))
        if not ok:
            self.valid = False

    def summary(self) -> str:
        # Show the detail only when a check fails; keep output ASCII-safe for consoles.
        lines = [
            f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  - {d}" if (d and not ok) else "")
            for name, ok, d in self.checks
        ]
        verdict = "VALID" if self.valid else "INVALID"
        return f"Receipt {verdict}\n" + "\n".join(lines)


def verify_receipt(receipt: dict[str, Any]) -> VerificationReport:
    report = VerificationReport()

    # 1. schema version
    version = receipt.get("schema_version")
    report.record(
        "schema_version supported",
        version == RECEIPT_SCHEMA_VERSION,
        f"got {version!r}, expected {RECEIPT_SCHEMA_VERSION!r}",
    )

    # 2. required top-level fields
    required = [
        "receipt_id", "request", "subjects", "authorization", "execution",
        "actions_root", "policy", "decision", "issued_at", "issuer",
        "receipt_hash", "signatures",
    ]
    missing = [f for f in required if f not in receipt]
    report.record("required fields present", not missing, f"missing: {missing}" if missing else "")

    # If structurally broken, stop before cryptographic checks.
    if missing or "receipt_hash" not in receipt or "signatures" not in receipt:
        return report

    # 3. receipt_hash integrity (T-1, INV-14)
    message = canonical_bytes(_payload(receipt))
    recomputed = hash_bytes(message).value
    report.record(
        "receipt_hash matches payload",
        recomputed == receipt.get("receipt_hash"),
        "payload was altered" if recomputed != receipt.get("receipt_hash") else "",
    )

    # 4. at least one valid signature (INV-13, INV-15)
    sigs = receipt.get("signatures") or []
    valid_sig = False
    for raw in sigs:
        try:
            if verify(Signature.from_dict(raw), message):
                valid_sig = True
                break
        except (KeyError, TypeError, ValueError):
            continue
    report.record("at least one valid signature", valid_sig)

    # 5. approvals bind to this execution + result (INV-9, T-6)
    execution_id = receipt.get("execution", {}).get("id")
    expected_rh = _expected_result_hash(receipt)
    approvals = receipt.get("approvals", [])
    approvals_ok = True
    detail = ""
    for ap in approvals:
        if ap.get("decision") != "approve":
            continue
        if ap.get("execution_id") != execution_id:
            approvals_ok = False
            detail = "an approval references a different execution (cross-execution)"
            break
        if ap.get("result_hash") != expected_rh:
            approvals_ok = False
            detail = "an approval's result_hash does not match this receipt's result"
            break
    report.record("approvals bind to this execution/result", approvals_ok, detail)

    # 5b. every 'approve' decision is validly signed by the claimed approver (INV-10)
    subjects_by_id = {s.get("id"): s for s in receipt.get("subjects", [])}
    sig_ok = True
    sig_detail = ""
    for ap in approvals:
        if ap.get("decision") != "approve":
            continue
        subject = subjects_by_id.get(ap.get("approver_subject_id"))
        approver_pub = subject.get("public_key") if subject else None
        if not verify_approval_signature(ap, approver_pub):
            sig_ok = False
            sig_detail = "an approval signature is missing, invalid, or not from the claimed approver"
            break
    report.record("approval signatures valid (approver identity)", sig_ok, sig_detail)

    # 5c. any revealed disclosures must match their signed commitments (redaction integrity)
    commitments = receipt.get("commitments", {})
    disclosures = receipt.get("disclosures", {})
    disclosures_ok = True
    disc_detail = ""
    for name, disclosure in disclosures.items():
        if name not in commitments or not verify_commitment(disclosure, commitments[name]):
            disclosures_ok = False
            disc_detail = f"disclosed field '{name}' does not match its commitment"
            break
    if disclosures or commitments:
        report.record("disclosures match commitments", disclosures_ok, disc_detail)

    # 6. ACCEPT requires an approval iff authorization/risk demanded one
    if receipt.get("decision") == "ACCEPT":
        auth = receipt.get("authorization", {})
        risk = receipt.get("request", {}).get("risk_class")
        needs_approval = bool(auth.get("requires_approval")) or risk in ("high", "critical")
        has_valid_approval = any(
            ap.get("decision") == "approve"
            and ap.get("execution_id") == execution_id
            and ap.get("result_hash") == expected_rh
            for ap in approvals
        )
        report.record(
            "ACCEPT has required approval",
            (not needs_approval) or has_valid_approval,
            "risk/authorization required a human approval that is absent (INV-16)"
            if needs_approval and not has_valid_approval else "",
        )

    return report
