"""T-11 — offline verification against static conformance vectors.

THREAT-MODEL §4 T-11: *"Verificar receipt sem acesso ao servidor -> sucesso (offline)."*

The receipts under ``tests/vectors/`` were signed on a different machine, at a different
time, by keys this process does not hold and cannot reach. Verifying them here therefore
exercises the property the product claims: a receipt is checkable using **only the receipt
file and the public key embedded in it** — no issuer, no policy engine, no key server, no
network, no shared state.

The guard at the bottom keeps that claim honest: this module must never import the issuer,
the policy engine or the scenario builder. If it did, "offline" would be a statement about
this test file rather than about the receipt.
"""

from __future__ import annotations

import copy
import json
import pathlib

from workattest.receipts.chain import verify_chain
from workattest.receipts.verifier import verify_receipt

VECTORS = pathlib.Path(__file__).resolve().parents[1] / "vectors"


def _load(name: str) -> dict:
    return json.loads((VECTORS / name).read_text(encoding="utf-8"))


def test_t11_standalone_vector_verifies_offline():
    assert verify_receipt(_load("receipt-accepted-v1.json")).valid


def test_t11_every_check_passes_on_the_vector():
    report = verify_receipt(_load("receipt-accepted-v1.json"))
    failed = [name for name, ok, _ in report.checks if not ok]
    assert failed == []


def test_t11_vector_carries_no_private_key_material():
    # A vector is published; it must never leak a signing key.
    raw = (VECTORS / "receipt-accepted-v1.json").read_text(encoding="utf-8").lower()
    for forbidden in ("private", "secret", "begin ", "seed"):
        assert forbidden not in raw


def test_t11_tampering_a_static_vector_is_detected():
    receipt = _load("receipt-accepted-v1.json")
    receipt["request"]["intent"] = "exfiltrate secrets"
    assert verify_receipt(receipt).valid is False


def test_t11_chain_vectors_verify_offline():
    chain = [_load("receipt-chain-001.json"), _load("receipt-chain-002.json")]
    assert verify_chain(chain).valid


def test_t11_reordering_the_chain_vectors_breaks_it():
    chain = [_load("receipt-chain-002.json"), _load("receipt-chain-001.json")]
    assert verify_chain(chain).valid is False


def test_t11_dropping_a_link_breaks_the_chain():
    chain = [_load("receipt-chain-002.json")]
    assert verify_chain(chain).valid is False


def test_t11_tampering_one_link_breaks_the_whole_chain():
    first = _load("receipt-chain-001.json")
    second = _load("receipt-chain-002.json")
    tampered = copy.deepcopy(first)
    tampered["decision"] = "REFUSE"
    assert verify_chain([tampered, second]).valid is False


def test_offline_claim_is_not_undermined_by_this_module():
    """Static guard: verifying must not need the issuing side of the system."""
    source = pathlib.Path(__file__).read_text(encoding="utf-8")
    imports = [
        line
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    ]
    forbidden = ("issuer", "scenario", "policy", "approval", "adapters")
    offenders = [
        line for line in imports if any(token in line for token in forbidden)
    ]
    assert offenders == [], f"offline vector tests must not import: {offenders}"
