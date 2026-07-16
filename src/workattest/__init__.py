"""WorkAttest — Verifiable Work Accountability.

Proof before acceptance. This package provides the deterministic core:
canonical serialization, hashing, Ed25519 signing, an append-only hash-chained
event log, a deterministic policy engine (ACCEPT/HOLD/REFUSE), and a receipt
issuer/verifier that is verifiable offline.

See docs/ACCOUNTABILITY-MODEL.md and docs/INVARIANTS.md for the contract this code
must uphold.
"""

__version__ = "0.1.0"

RECEIPT_SCHEMA_VERSION = "1.0.0"
