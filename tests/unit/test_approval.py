import copy

from workattest.approval import build_signed_approval, verify_approval_signature
from workattest.crypto.keys import KeyPair
from workattest.hashing import hash_canonical

RH = hash_canonical({"result": "x"})


def _approval(approver: KeyPair, subject_id="subj-human", exec_id="exec-1"):
    return build_signed_approval(
        execution_id=exec_id, approver_subject_id=subject_id, result_hash=RH,
        policy_id="pol", now="2026-01-01T00:00:00Z", approver_key=approver,
    ).to_dict()


def test_signed_approval_verifies_with_matching_key():
    kp = KeyPair.generate()
    ap = _approval(kp)
    assert verify_approval_signature(ap, kp.public_key_b64) is True


def test_verify_fails_with_wrong_registered_key():  # INV-10 identity binding
    ap = _approval(KeyPair.generate())
    assert verify_approval_signature(ap, KeyPair.generate().public_key_b64) is False


def test_verify_fails_when_payload_tampered():
    kp = KeyPair.generate()
    ap = _approval(kp)
    ap["justification"] = "forged"
    assert verify_approval_signature(ap, kp.public_key_b64) is False


def test_verify_fails_when_signature_stripped():
    kp = KeyPair.generate()
    ap = _approval(kp)
    ap.pop("signature")
    assert verify_approval_signature(ap, kp.public_key_b64) is False


def test_verify_accepts_when_registered_key_unknown_but_signature_valid():
    # When the approver's registered key isn't provided, a structurally valid signature
    # still verifies (identity binding is enforced separately by the receipt verifier).
    kp = KeyPair.generate()
    ap = _approval(kp)
    assert verify_approval_signature(ap, None) is True
