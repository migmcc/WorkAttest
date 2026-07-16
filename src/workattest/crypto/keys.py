"""Ed25519 key handling."""

from __future__ import annotations

import base64
from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def _b64e(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _b64d(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"))


def public_key_b64(key: Ed25519PublicKey) -> str:
    raw = key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return _b64e(raw)


def load_public_key(b64: str) -> Ed25519PublicKey:
    return Ed25519PublicKey.from_public_bytes(_b64d(b64))


@dataclass(frozen=True)
class KeyPair:
    """An Ed25519 key pair with a stable ``key_id`` derived from the public key."""

    private_key: Ed25519PrivateKey
    key_id: str

    @classmethod
    def generate(cls, key_id: str | None = None) -> "KeyPair":
        priv = Ed25519PrivateKey.generate()
        kid = key_id or cls._derive_key_id(priv.public_key())
        return cls(private_key=priv, key_id=kid)

    @staticmethod
    def _derive_key_id(pub: Ed25519PublicKey) -> str:
        import hashlib

        raw = pub.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return "ed25519:" + hashlib.sha256(raw).hexdigest()[:16]

    @property
    def public_key(self) -> Ed25519PublicKey:
        return self.private_key.public_key()

    @property
    def public_key_b64(self) -> str:
        return public_key_b64(self.public_key)

    # --- private key persistence (MVP: unencrypted PEM; enterprise: HSM/KMS) ---
    def private_bytes_pem(self) -> bytes:
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

    @classmethod
    def from_pem(cls, pem: bytes, key_id: str | None = None) -> "KeyPair":
        priv = serialization.load_pem_private_key(pem, password=None)
        if not isinstance(priv, Ed25519PrivateKey):
            raise ValueError("not an Ed25519 private key")
        kid = key_id or cls._derive_key_id(priv.public_key())
        return cls(private_key=priv, key_id=kid)
