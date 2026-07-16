"""Authenticated human approval.

An approval is a human accepting *exactly one* execution's result. It binds to the
execution id and the result hash (INV-9) and is signed by the approver's key, so the
approver's identity derives from authentication, not from a claimed name (INV-10). The
signature covers the canonical approval payload with the ``signature`` field removed —
the same construction used for receipts.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Optional

from .canonical import canonical_bytes
from .crypto.keys import KeyPair
from .crypto.signing import Signature, sign, verify
from .domain.entities import ApprovalDecision
from .hashing import HashRef
from .ids import new_id


def approval_message(approval: dict) -> bytes:
    """Canonical bytes an approval signature covers (payload without the signature)."""
    payload = {k: v for k, v in approval.items() if k != "signature"}
    return canonical_bytes(payload)


def build_signed_approval(
    *,
    execution_id: str,
    approver_subject_id: str,
    result_hash: HashRef,
    policy_id: str,
    now: str,
    approver_key: KeyPair,
    decision: str = "approve",
    justification: Optional[str] = None,
    role: Optional[str] = None,
    approval_id: Optional[str] = None,
) -> ApprovalDecision:
    """Build an ApprovalDecision signed by ``approver_key``."""
    unsigned = ApprovalDecision(
        id=approval_id or new_id("apr"),
        execution_id=execution_id,
        approver_subject_id=approver_subject_id,
        decision=decision,
        result_hash=result_hash,
        policy_id=policy_id,
        decided_at=now,
        role=role,
        justification=justification,
        signature=None,
    )
    message = canonical_bytes(unsigned.to_dict())
    signature = sign(approver_key, message, created_at=now).to_dict()
    return replace(unsigned, signature=signature)


def verify_approval_signature(approval: dict, approver_public_key_b64: Optional[str]) -> bool:
    """Verify an approval's signature and that it was made by the claimed approver's key.

    Returns True only if the signature is valid over the approval payload *and*, when the
    approver's registered public key is known, the signing key matches it (INV-10).
    """
    sig_raw = approval.get("signature")
    if not sig_raw:
        return False
    try:
        signature = Signature.from_dict(sig_raw)
    except (KeyError, TypeError):
        return False
    if not verify(signature, approval_message(approval)):
        return False
    if approver_public_key_b64 is not None and signature.public_key != approver_public_key_b64:
        return False
    return True
