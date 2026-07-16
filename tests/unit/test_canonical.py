import pytest

from workattest.canonical import CanonicalizationError, canonical_bytes, canonicalize


def test_key_order_is_deterministic():
    a = {"b": 1, "a": 2, "c": {"z": 1, "y": 2}}
    b = {"c": {"y": 2, "z": 1}, "a": 2, "b": 1}
    assert canonicalize(a) == canonicalize(b)


def test_no_insignificant_whitespace():
    assert canonicalize({"a": 1, "b": [1, 2]}) == '{"a":1,"b":[1,2]}'


def test_non_ascii_is_utf8_not_escaped():
    assert canonicalize({"k": "ção"}) == '{"k":"ção"}'
    assert "\\u" not in canonicalize({"k": "ção"})


def test_floats_are_rejected():
    with pytest.raises(CanonicalizationError):
        canonicalize({"x": 1.5})


def test_unsupported_type_rejected():
    with pytest.raises(CanonicalizationError):
        canonicalize({"x": {1, 2, 3}})


def test_canonical_bytes_is_utf8():
    assert canonical_bytes({"k": "ç"}) == '{"k":"ç"}'.encode("utf-8")
