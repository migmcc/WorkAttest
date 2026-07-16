import copy

import pytest

from workattest.redaction import (
    commit,
    make_disclosure,
    open_disclosure,
    redact_receipt,
    verify_commitment,
)
from workattest.receipts.verifier import verify_receipt
from workattest.scenario import build_accepted_receipt

FIELD = "reviewer_note"


def test_commitment_roundtrip():
    c, disc = make_disclosure("secret")
    assert verify_commitment(disc, c) is True


def test_commitment_is_salted():
    # same value, different salt -> different commitment (salt hides low-entropy values)
    c1, _ = make_disclosure("yes")
    c2, _ = make_disclosure("yes")
    assert c1 != c2


def test_wrong_value_fails_commitment():
    c, disc = make_disclosure("real")
    disc["value"] = "fake"
    assert verify_commitment(disc, c) is False


def test_wrong_salt_fails_commitment():
    c, disc = make_disclosure("real")
    disc["salt"] = "AAAAAAAAAAAAAAAAAAAAAA=="
    assert verify_commitment(disc, c) is False


def test_receipt_with_disclosure_is_valid_and_openable():
    receipt = build_accepted_receipt().receipt
    assert verify_receipt(receipt).valid
    value = open_disclosure(receipt, FIELD)
    assert "hardcoded token" in value


def test_redacted_receipt_still_verifies():  # INV-19
    receipt = build_accepted_receipt().receipt
    redacted = redact_receipt(receipt, [FIELD])
    report = verify_receipt(redacted)
    assert report.valid, report.summary()
    assert "disclosures" not in redacted or FIELD not in redacted.get("disclosures", {})
    # the commitment remains as proof the field existed
    assert FIELD in redacted["commitments"]


def test_open_redacted_field_raises_lookup():
    redacted = redact_receipt(build_accepted_receipt().receipt, [FIELD])
    with pytest.raises(LookupError):
        open_disclosure(redacted, FIELD)


def test_tampered_disclosure_fails_verification():
    receipt = build_accepted_receipt().receipt
    receipt["disclosures"][FIELD]["value"] = "forged note"
    report = verify_receipt(receipt)
    assert report.valid is False
    assert any("disclosures match commitments" in name and not ok for name, ok, _ in report.checks)


def test_redaction_does_not_change_receipt_hash_or_signature():
    receipt = build_accepted_receipt().receipt
    redacted = redact_receipt(receipt, [FIELD])
    assert redacted["receipt_hash"] == receipt["receipt_hash"]
    assert redacted["signatures"] == receipt["signatures"]
