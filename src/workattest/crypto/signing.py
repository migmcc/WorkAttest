"""Detached Ed25519 signatures over arbitrary bytes."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, Optional

from cryptography.exceptions import InvalidSignature

from .keys import KeyPair, load_public_key, public_key_b64


def _b64e(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _b64d(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"))


@dataclass(frozen=True)
class Signature:
    alg: str
    key_id: str
    public_key: str
    value: str
    created_at: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        data = {
            "alg": self.alg,
            "key_id": self.key_id,
            "public_key": self.public_key,
            "value": self.value,
        }
        if self.created_at is not None:
            data["created_at"] = self.created_at
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Signature":
        return cls(
            alg=data["alg"],
            key_id=data["key_id"],
            public_key=data["public_key"],
            value=data["value"],
            created_at=data.get("created_at"),
        )


def sign(keypair: KeyPair, message: bytes, created_at: Optional[str] = None) -> Signature:
    raw_sig = keypair.private_key.sign(message)
    return Signature(
        alg="ed25519",
        key_id=keypair.key_id,
        public_key=keypair.public_key_b64,
        value=_b64e(raw_sig),
        created_at=created_at,
    )


def verify(signature: Signature, message: bytes) -> bool:
    """Verify a signature offline using the public key embedded in it (INV-15)."""
    if signature.alg != "ed25519":
        return False
    try:
        pub = load_public_key(signature.public_key)
        pub.verify(_b64d(signature.value), message)
        return True
    except (InvalidSignature, ValueError):
        # verify() must never raise on bad input — a malformed key/sig is just invalid.
        return False
