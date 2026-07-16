import pytest

from workattest.hashing import HashRef, hash_bytes, hash_canonical


def test_hash_is_stable_across_key_order():
    assert hash_canonical({"a": 1, "b": 2}) == hash_canonical({"b": 2, "a": 1})


def test_hash_changes_with_content():
    assert hash_canonical({"a": 1}) != hash_canonical({"a": 2})


def test_hashref_roundtrip():
    h = hash_bytes(b"hello")
    assert HashRef.from_dict(h.to_dict()) == h
    assert h.alg == "sha256"
    assert len(h.value) == 64


def test_unsupported_alg():
    with pytest.raises(ValueError):
        hash_bytes(b"x", alg="md5")
