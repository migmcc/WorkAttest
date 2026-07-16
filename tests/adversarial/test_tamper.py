"""Adversarial tests — every mitigation must FAIL the receipt when attacked.

Maps to docs/THREAT-MODEL.md §4 (T-1, T-2, T-6, T-9) and the invariants they defend.
"""

import copy

from workattest.receipts.verifier import verify_receipt
from workattest.scenario import build_accepted_receipt


def _receipt():
    return copy.deepcopy(build_accepted_receipt().receipt)


def test_baseline_is_valid():
    assert verify_receipt(_receipt()).valid


def test_t1_flip_a_field_after_signing():  # T-1 / INV-14
    r = _receipt()
    r["request"]["intent"] = "exfiltrate secrets"
    assert verify_receipt(r).valid is False


def test_t1_edit_receipt_hash_directly():  # T-1
    r = _receipt()
    r["receipt_hash"] = "0" * 64
    assert verify_receipt(r).valid is False


def test_t2_swap_an_artifact_hash():  # T-2 / INV-6
    r = _receipt()
    r["artifacts"][0]["after_hash"]["value"] = "f" * 64
    assert verify_receipt(r).valid is False


def test_strip_signatures():  # INV-13
    r = _receipt()
    r["signatures"] = []
    assert verify_receipt(r).valid is False


def test_forge_signature_value():  # INV-13
    r = _receipt()
    r["signatures"][0]["value"] = "AAAA"
    assert verify_receipt(r).valid is False


def test_t6_cross_execution_approval():  # T-6 / INV-9
    r = _receipt()
    r["approvals"][0]["execution_id"] = "some-other-execution"
    # This also changes payload → hash+sig break; the approval-binding check adds defense in depth.
    assert verify_receipt(r).valid is False


def test_t6_approval_result_hash_mismatch_detected_by_binding():  # T-6 / INV-9
    # Rebuild with a valid signature over a tampered approval result_hash to prove the
    # binding check (not only the signature) rejects cross-execution reuse.
    from workattest.crypto.keys import KeyPair
    from workattest.canonical import canonical_bytes
    from workattest.crypto.signing import sign
    from workattest.hashing import hash_bytes

    r = _receipt()
    r["approvals"][0]["result_hash"] = {"alg": "sha256", "value": "1" * 64}
    # Re-sign so the signature is valid over the tampered payload:
    payload = {k: v for k, v in r.items() if k not in ("signatures", "receipt_hash", "disclosures")}
    msg = canonical_bytes(payload)
    r["receipt_hash"] = hash_bytes(msg).value
    r["signatures"] = [sign(KeyPair.generate(), msg).to_dict()]

    report = verify_receipt(r)
    # Signature + hash now pass, but the approval no longer binds to the real result.
    assert report.valid is False
    assert any("approval" in name and not ok for name, ok, _ in report.checks)


def test_wrong_schema_version():
    r = _receipt()
    r["schema_version"] = "9.9.9"
    assert verify_receipt(r).valid is False


def test_forge_approval_by_swapping_signer_key():  # INV-10
    # Re-sign the whole receipt (so receipt_hash + signature pass) but leave the approval
    # signed by a key that does not match the registered approver subject. The approval
    # signature / identity check must still reject it.
    from workattest.approval import build_signed_approval
    from workattest.canonical import canonical_bytes
    from workattest.crypto.keys import KeyPair
    from workattest.crypto.signing import sign
    from workattest.hashing import HashRef, hash_bytes

    r = _receipt()
    execution_id = r["execution"]["id"]
    # a valid signature, but from an attacker key that isn't the registered approver
    attacker = KeyPair.generate()
    forged = build_signed_approval(
        execution_id=execution_id, approver_subject_id="subj-human",
        result_hash=HashRef.from_dict(r["approvals"][0]["result_hash"]),
        policy_id=r["approvals"][0]["policy_id"], now=r["issued_at"], approver_key=attacker,
    ).to_dict()
    r["approvals"] = [forged]
    payload = {k: v for k, v in r.items() if k not in ("signatures", "receipt_hash", "disclosures")}
    msg = canonical_bytes(payload)
    r["receipt_hash"] = hash_bytes(msg).value
    r["signatures"] = [sign(KeyPair.generate(), msg).to_dict()]

    report = verify_receipt(r)
    # receipt_hash + signature now genuinely pass; only the approver-identity check catches it.
    assert report.valid is False
    assert any("approval signatures valid" in name and not ok for name, ok, _ in report.checks)
    assert all(ok for name, ok, _ in report.checks if name in ("receipt_hash matches payload", "at least one valid signature"))
