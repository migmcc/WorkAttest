"""Identifier generation.

MVP uses UUIDv4 for entity ids. Ids are opaque and must not encode trust; identity
and authority derive from keys and signatures, never from an id string.
"""

from __future__ import annotations

import uuid


def new_id(prefix: str = "") -> str:
    value = uuid.uuid4().hex
    return f"{prefix}_{value}" if prefix else value
