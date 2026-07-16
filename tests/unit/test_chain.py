import copy

from workattest.receipts import verify_chain
from workattest.scenario import build_accepted_receipt


def _chain(n: int) -> list[dict]:
    receipts: list[dict] = []
    prev = None
    for i in range(n):
        r = build_accepted_receipt(receipt_id=f"rcpt-{i}", previous_receipt_hash=prev).receipt
        receipts.append(r)
        prev = r["receipt_hash"]
    return receipts


def test_valid_chain():
    report = verify_chain(_chain(3))
    assert report.valid, report.summary()


def test_single_root_is_valid():
    assert verify_chain(_chain(1)).valid


def test_empty_chain_is_invalid():
    assert verify_chain([]).valid is False


def test_root_must_not_reference_parent():
    chain = _chain(2)
    chain[0]["previous_receipt_hash"] = "deadbeef"  # breaks root's own hash too
    assert verify_chain(chain).valid is False


def test_broken_link_detected():
    chain = _chain(3)
    # Point the middle receipt at the wrong parent by rebuilding the list out of order.
    chain[2], chain[1] = chain[1], chain[2]
    assert verify_chain(chain).valid is False


def test_tampered_middle_receipt_detected():
    chain = _chain(3)
    chain[1] = copy.deepcopy(chain[1])
    chain[1]["request"]["intent"] = "tampered"
    report = verify_chain(chain)
    assert report.valid is False
    # receipt[1] fails individually; receipt[2]'s link no longer matches either.
    assert any(i == 1 and not ok for i, ok, _ in report.links)


def test_inserting_a_foreign_receipt_breaks_chain():
    chain = _chain(2)
    foreign = build_accepted_receipt(receipt_id="foreign").receipt  # no parent link
    chain.insert(1, foreign)
    assert verify_chain(chain).valid is False
