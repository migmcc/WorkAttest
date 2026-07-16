from workattest.domain.enums import Decision
from workattest.receipts.issuer import compute_receipt_hash
from workattest.receipts.verifier import verify_receipt
from workattest.scenario import build_accepted_receipt


def test_demo_receipt_is_accept():
    result = build_accepted_receipt()
    assert result.decision is Decision.ACCEPT


def test_valid_receipt_verifies_offline():
    receipt = build_accepted_receipt().receipt
    report = verify_receipt(receipt)
    assert report.valid, report.summary()


def test_receipt_has_signature_and_hash():  # INV-13
    receipt = build_accepted_receipt().receipt
    assert receipt["signatures"]
    assert len(receipt["receipt_hash"]) == 64


def test_receipt_hash_reproduces_from_payload():  # INV-12 / INV-14
    # Recomputing the hash of a receipt's own payload must reproduce receipt_hash,
    # independent of key insertion order. (Two independent builds differ only because
    # the demo mints fresh keys each time — that is correct, not a determinism bug.)
    receipt = build_accepted_receipt().receipt
    assert compute_receipt_hash(receipt).value == receipt["receipt_hash"]
