"""Receipt chains — verifiable audit lineage.

Receipts can form an append-only chain: each non-root receipt's ``previous_receipt_hash``
commits to the ``receipt_hash`` of its predecessor. Because ``receipt_hash`` covers the
whole payload (which includes ``previous_receipt_hash``), altering, reordering, inserting,
or deleting any receipt in the chain breaks a link. A chain is valid only if every receipt
is individually valid AND every link matches.

Use cases: a release receipt chaining from the change receipts it bundles; a sequence of
approvals over the life of a work item.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from .verifier import verify_receipt


@dataclass
class ChainReport:
    valid: bool = True
    links: list[tuple[int, bool, str]] = field(default_factory=list)

    def record(self, index: int, ok: bool, detail: str = "") -> None:
        self.links.append((index, ok, detail))
        if not ok:
            self.valid = False

    def summary(self) -> str:
        lines = [
            f"{'PASS' if ok else 'FAIL'}  receipt[{i}]" + (f"  - {d}" if (d and not ok) else "")
            for i, ok, d in self.links
        ]
        verdict = "VALID" if self.valid else "INVALID"
        return f"Chain {verdict} ({len(self.links)} receipts)\n" + "\n".join(lines)


def verify_chain(receipts: Sequence[dict[str, Any]]) -> ChainReport:
    """Verify an ordered list of receipts (root first) as a chain."""
    report = ChainReport()
    if not receipts:
        report.record(0, False, "empty chain")
        return report

    previous_hash: str | None = None
    for index, receipt in enumerate(receipts):
        individual = verify_receipt(receipt)
        if not individual.valid:
            report.record(index, False, "receipt is individually invalid")
            previous_hash = receipt.get("receipt_hash")
            continue

        link_prev = receipt.get("previous_receipt_hash")
        if index == 0:
            ok = link_prev is None
            report.record(index, ok, "" if ok else "root receipt must not reference a parent")
        else:
            ok = link_prev == previous_hash
            report.record(
                index, ok,
                "" if ok else "previous_receipt_hash does not match the prior receipt",
            )
        previous_hash = receipt.get("receipt_hash")

    return report
