"""Assemble, hash and sign a WorkReceipt.

The signature covers the canonical serialization of the receipt payload with the
``signatures`` and ``receipt_hash`` fields removed. ``receipt_hash`` is the hash of that
same payload. Verifying reconstructs the payload identically, so any change to any
covered field breaks both the hash check and the signature (INV-14, T-1).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

from .. import RECEIPT_SCHEMA_VERSION
from ..canonical import canonical_bytes
from ..redaction import make_disclosure
from ..crypto.keys import KeyPair
from ..crypto.signing import Signature, sign
from ..domain.entities import (
    ApprovalDecision,
    ArtifactEvidence,
    Authorization,
    ExecutionSession,
    PolicyRef,
    Subject,
    VerificationResult,
    WorkRequest,
)
from ..domain.enums import Decision
from ..hashing import HashRef, hash_bytes, hash_canonical
from ..ids import new_id

# Fields excluded from the signed/hashed payload. 'disclosures' carries redactable
# plaintext+salt and must stay outside the signature so redaction preserves validity.
_UNCOVERED = ("signatures", "receipt_hash", "disclosures")


def _payload(receipt: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in receipt.items() if k not in _UNCOVERED}


def compute_receipt_hash(receipt: dict[str, Any]) -> HashRef:
    """Hash of the receipt payload excluding signatures and receipt_hash."""
    return hash_bytes(canonical_bytes(_payload(receipt)))


def result_hash_of(
    *,
    execution: ExecutionSession,
    artifacts: Sequence[ArtifactEvidence],
    verification: Sequence[VerificationResult],
    actions_root: str,
) -> HashRef:
    """Hash identifying the exact result an approver accepts (binds INV-9).

    Deterministic over the execution, its artifacts, its verification results, and the
    action-log root — i.e. *what* was produced and verified, not the receipt envelope.
    """
    material = {
        "execution": execution.to_dict(),
        "artifacts": [a.to_dict() for a in artifacts],
        "verification": [v.to_dict() for v in verification],
        "actions_root": actions_root,
    }
    return hash_canonical(material)


@dataclass
class ReceiptBuilder:
    request: WorkRequest
    subjects: Sequence[Subject]
    authorization: Authorization
    execution: ExecutionSession
    actions_root: str
    policy: PolicyRef
    decision: Decision
    artifacts: Sequence[ArtifactEvidence] = field(default_factory=tuple)
    verification: Sequence[VerificationResult] = field(default_factory=tuple)
    approvals: Sequence[ApprovalDecision] = field(default_factory=tuple)
    issued_at: str = ""
    issuer: str = "workattest"
    receipt_id: Optional[str] = None
    previous_receipt_hash: Optional[str] = None
    # name -> sensitive value; committed (signed) and disclosed (unsigned) so it can be redacted.
    redactable: Optional[Mapping[str, Any]] = None

    def _base(self) -> dict[str, Any]:
        receipt: dict[str, Any] = {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "receipt_id": self.receipt_id or new_id("rcpt"),
            "request": self.request.to_dict(),
            "subjects": [s.to_dict() for s in self.subjects],
            "authorization": self.authorization.to_dict(),
            "execution": self.execution.to_dict(),
            "actions_root": self.actions_root,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "verification": [v.to_dict() for v in self.verification],
            "policy": self.policy.to_dict(),
            "decision": self.decision.value,
            "issued_at": self.issued_at,
            "issuer": self.issuer,
            "previous_receipt_hash": self.previous_receipt_hash,
        }
        if self.approvals:
            receipt["approvals"] = [a.to_dict() for a in self.approvals]
        return receipt

    def build_signed(self, keypairs: Sequence[KeyPair]) -> dict[str, Any]:
        """Return a fully-formed, signed receipt dict (INV-13 requires >=1 signature)."""
        if not keypairs:
            raise ValueError("at least one signing key is required (INV-13)")
        receipt = self._base()

        disclosures: dict[str, Any] = {}
        if self.redactable:
            commitments: dict[str, str] = {}
            for name, value in self.redactable.items():
                commitment, disclosure = make_disclosure(value)
                commitments[name] = commitment   # signed
                disclosures[name] = disclosure   # unsigned sidecar
            receipt["commitments"] = commitments

        message = canonical_bytes(_payload(receipt))
        receipt["receipt_hash"] = hash_bytes(message).value
        signatures = [sign(kp, message, created_at=self.issued_at).to_dict() for kp in keypairs]
        receipt["signatures"] = signatures
        if disclosures:
            receipt["disclosures"] = disclosures  # excluded from the signature by _UNCOVERED
        return receipt
