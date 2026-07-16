"""Canonical JSON serialization (RFC 8785 / JCS subset).

Deterministic serialization is the foundation of every hash and signature in
WorkAttest (INV-12). Two structurally-equal payloads MUST produce byte-identical
output regardless of key insertion order.

MVP scope and guarantees:
- Object keys are sorted lexicographically by Unicode code point.
- No insignificant whitespace; ``","`` and ``":"`` separators.
- Strings use standard JSON escaping; non-ASCII is emitted as UTF-8 (not \\u escaped).
- Only JSON-safe types are accepted: dict, list, str, bool, int, None.

Floats are **rejected**. RFC 8785 number canonicalization (ES6
``Number.prototype.toString``) is subtle and a common source of cross-implementation
drift; the WorkReceipt schema uses only integers (sizes) and strings (hashes,
timestamps), so forbidding floats keeps determinism provable. If real-number fields
are ever needed, add them as canonicalized decimal strings, not floats.
"""

from __future__ import annotations

import json
from typing import Any


class CanonicalizationError(ValueError):
    """Raised when a value cannot be canonicalized deterministically."""


def _check(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, float):
        raise CanonicalizationError(
            f"float at {path} is not allowed (non-deterministic); use int or a decimal string"
        )
    if isinstance(value, int):
        return
    if isinstance(value, dict):
        for key, val in value.items():
            if not isinstance(key, str):
                raise CanonicalizationError(f"non-string object key at {path}: {key!r}")
            _check(val, f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            _check(item, f"{path}[{i}]")
        return
    raise CanonicalizationError(f"unsupported type at {path}: {type(value).__name__}")


def canonicalize(value: Any) -> str:
    """Return the canonical JSON string for ``value``.

    Raises :class:`CanonicalizationError` for unsupported or non-deterministic types.
    """
    _check(value)
    # bool is a subclass of int; json handles it correctly. sort_keys sorts by
    # Python string comparison, which is code-point order for str keys.
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )


def canonical_bytes(value: Any) -> bytes:
    """Return the UTF-8 encoding of the canonical JSON for ``value``."""
    return canonicalize(value).encode("utf-8")
