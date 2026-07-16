"""Redactable fields via salted hash commitments.

A sensitive value is committed in the *signed* part of a receipt as
``commitment = sha256(canonical({"salt", "value"}))`` and stored — together with its
salt — in an *unsigned* ``disclosures`` sidecar. Because only the commitment is signed:

- **Redacting** a field means dropping its disclosure. The commitment stays, the receipt
  still verifies, and the value is provably gone (INV-19, data minimization).
- **Disclosing** a field means revealing ``(salt, value)``; anyone recomputes the
  commitment and confirms it matches the signed one — so a disclosure cannot be forged.

The salt (128-bit random) stops an attacker brute-forcing a low-entropy value from its
commitment. ``disclosures`` is excluded from the signed payload (see receipts.issuer /
receipts.verifier ``_UNCOVERED``), so adding or removing disclosures never changes
``receipt_hash`` or the signatures.
"""

from __future__ import annotations

import base64
import copy
import secrets
from typing import Any, Iterable

from .hashing import hash_canonical

_SALT_BYTES = 16


def new_salt() -> str:
    return base64.b64encode(secrets.token_bytes(_SALT_BYTES)).decode("ascii")


def commit(value: Any, salt: str) -> str:
    """Return the commitment hex for ``value`` under ``salt``."""
    return hash_canonical({"salt": salt, "value": value}).value


def make_disclosure(value: Any, salt: str | None = None) -> tuple[str, dict[str, Any]]:
    """Return ``(commitment, disclosure)`` where disclosure is ``{"salt", "value"}``."""
    salt = salt or new_salt()
    return commit(value, salt), {"salt": salt, "value": value}


def verify_commitment(disclosure: dict[str, Any], commitment: str) -> bool:
    """Check a revealed ``{"salt","value"}`` disclosure against a commitment."""
    try:
        return commit(disclosure["value"], disclosure["salt"]) == commitment
    except (KeyError, TypeError):
        return False


def redact_receipt(receipt: dict[str, Any], names: Iterable[str]) -> dict[str, Any]:
    """Return a copy of ``receipt`` with the named disclosures removed.

    The commitments (signed) are preserved, so the redacted receipt still verifies and
    still proves those fields existed — their values are simply withheld.
    """
    redacted = copy.deepcopy(receipt)
    disclosures = redacted.get("disclosures", {})
    for name in names:
        disclosures.pop(name, None)
    if not disclosures:
        redacted.pop("disclosures", None)
    else:
        redacted["disclosures"] = disclosures
    return redacted


def open_disclosure(receipt: dict[str, Any], name: str) -> Any:
    """Return the disclosed value for ``name`` if present and its commitment matches.

    Raises ``KeyError`` if the field is unknown, ``LookupError`` if redacted (commitment
    present but no disclosure), or ``ValueError`` if the disclosure fails its commitment.
    """
    commitments = receipt.get("commitments", {})
    if name not in commitments:
        raise KeyError(f"no committed field named {name!r}")
    disclosures = receipt.get("disclosures", {})
    if name not in disclosures:
        raise LookupError(f"field {name!r} is redacted (commitment only)")
    disclosure = disclosures[name]
    if not verify_commitment(disclosure, commitments[name]):
        raise ValueError(f"disclosure for {name!r} does not match its commitment")
    return disclosure["value"]
