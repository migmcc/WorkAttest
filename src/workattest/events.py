"""Append-only, hash-chained action event log (INV-4, INV-11).

Each event is chained to the previous by including the previous entry's hash in the
canonical payload that is hashed. Any insertion, deletion, or modification anywhere in
the chain changes every subsequent hash, so tampering is detectable (maps to
THREAT-MODEL T-3). Events record what an *authorized source* observed — never the
agent's self-report.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional

from .hashing import HashRef, hash_canonical

GENESIS = "0" * 64  # previous_event_hash for the first entry


@dataclass(frozen=True)
class ActionEvent:
    sequence: int
    action_type: str
    resource: str
    observed_by: str
    occurred_at: str
    parameters_hash: Optional[HashRef] = None
    result_hash: Optional[HashRef] = None

    def payload(self, previous_event_hash: str) -> dict[str, Any]:
        data: dict[str, Any] = {
            "sequence": self.sequence,
            "action_type": self.action_type,
            "resource": self.resource,
            "observed_by": self.observed_by,
            "occurred_at": self.occurred_at,
            "previous_event_hash": previous_event_hash,
        }
        if self.parameters_hash is not None:
            data["parameters_hash"] = self.parameters_hash.to_dict()
        if self.result_hash is not None:
            data["result_hash"] = self.result_hash.to_dict()
        return data


@dataclass
class _Entry:
    event: ActionEvent
    previous_event_hash: str
    entry_hash: str


class EventLog:
    """An append-only hash chain of action events."""

    def __init__(self) -> None:
        self._entries: list[_Entry] = []

    @property
    def head(self) -> str:
        """Hash of the last entry, or GENESIS if empty."""
        return self._entries[-1].entry_hash if self._entries else GENESIS

    @property
    def actions_root(self) -> str:
        """Root committed into the receipt. MVP: the chain head hash."""
        return self.head

    def __len__(self) -> int:
        return len(self._entries)

    def append(
        self,
        action_type: str,
        resource: str,
        observed_by: str,
        occurred_at: str,
        parameters_hash: Optional[HashRef] = None,
        result_hash: Optional[HashRef] = None,
    ) -> str:
        prev = self.head
        event = ActionEvent(
            sequence=len(self._entries),
            action_type=action_type,
            resource=resource,
            observed_by=observed_by,
            occurred_at=occurred_at,
            parameters_hash=parameters_hash,
            result_hash=result_hash,
        )
        entry_hash = hash_canonical(event.payload(prev)).value
        self._entries.append(_Entry(event=event, previous_event_hash=prev, entry_hash=entry_hash))
        return entry_hash

    def to_list(self) -> list[dict[str, Any]]:
        return [
            {**e.event.payload(e.previous_event_hash), "entry_hash": e.entry_hash}
            for e in self._entries
        ]

    @staticmethod
    def verify_chain(entries: Iterable[dict[str, Any]]) -> bool:
        """Recompute the chain and confirm every link and head are intact (T-3)."""
        prev = GENESIS
        expected_seq = 0
        for entry in entries:
            if entry.get("previous_event_hash") != prev:
                return False
            if entry.get("sequence") != expected_seq:
                return False
            payload = {k: v for k, v in entry.items() if k != "entry_hash"}
            recomputed = hash_canonical(payload).value
            if recomputed != entry.get("entry_hash"):
                return False
            prev = entry["entry_hash"]
            expected_seq += 1
        return True
