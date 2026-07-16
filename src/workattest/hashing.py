"""Content hashing over canonical JSON.

Every artifact, check definition, policy and receipt is identified by a hash of its
canonical serialization. A :class:`HashRef` is the ``{alg, value}`` pair used
throughout the receipt schema.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from .canonical import canonical_bytes

_ALGS = {
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
}


@dataclass(frozen=True)
class HashRef:
    """A hash reference: algorithm + hex digest."""

    alg: str
    value: str

    def __post_init__(self) -> None:
        if self.alg not in _ALGS:
            raise ValueError(f"unsupported hash alg: {self.alg}")

    def to_dict(self) -> dict[str, str]:
        return {"alg": self.alg, "value": self.value}

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "HashRef":
        return cls(alg=data["alg"], value=data["value"])


def hash_bytes(data: bytes, alg: str = "sha256") -> HashRef:
    try:
        fn = _ALGS[alg]
    except KeyError as exc:
        raise ValueError(f"unsupported hash alg: {alg}") from exc
    return HashRef(alg=alg, value=fn(data).hexdigest())


def hash_canonical(value: Any, alg: str = "sha256") -> HashRef:
    """Hash the canonical serialization of ``value`` (INV-6, INV-7, INV-12)."""
    return hash_bytes(canonical_bytes(value), alg=alg)
