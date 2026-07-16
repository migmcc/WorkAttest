"""Cryptography: Ed25519 keys and detached signatures.

Signatures enable offline verification with only a public key (INV-13, INV-15). Keys
are serialized as base64-encoded raw 32-byte values so a receipt carries everything a
third party needs to verify it without contacting the issuer.
"""

from .keys import KeyPair, load_public_key, public_key_b64
from .signing import Signature, sign, verify

__all__ = [
    "KeyPair",
    "Signature",
    "sign",
    "verify",
    "load_public_key",
    "public_key_b64",
]
