# Conformance vectors

Static, signed WorkAttest receipts. They exist to prove — and to let anyone else prove —
that a receipt verifies **without the system that issued it**.

| File | What it is |
| --- | --- |
| `receipt-accepted-v1.json` | A standalone `ACCEPT` receipt, schema v1. |
| `receipt-chain-001.json` | Root of a two-link chain (`previous_receipt_hash: null`). |
| `receipt-chain-002.json` | Second link; commits to the `receipt_hash` of the root. |

## Why they are committed

Every other test in this repository builds a receipt and then checks it, so the issuer and
the verifier always agree by construction. These vectors break that loop: they were signed
on one machine, by keys that no longer exist anywhere, and are verified on another — in CI,
on Linux, macOS and Windows. That is the claim in the README (*"Verify a receipt on ANY
machine, using only the public key inside it"*) turned into something continuously tested
rather than asserted.

They map to **T-11** in [`docs/THREAT-MODEL.md`](../../docs/THREAT-MODEL.md) §4.

## Verifying them yourself

```bash
workattest receipt verify tests/vectors/receipt-accepted-v1.json
workattest receipt verify-chain tests/vectors/receipt-chain-001.json tests/vectors/receipt-chain-002.json
```

No key material, no configuration and no network access is required. If you are writing an
independent verifier — in another language, for example — these files are the contract to
verify against: an implementation that accepts all three, and rejects any single-byte
mutation of them, is conformant with receipt schema v1.

## What they must never contain

Public keys only. A vector carrying private key material would hand an attacker the ability
to forge receipts; `tests/adversarial/test_offline_vectors.py` asserts this on every run.

## Regenerating

Vectors are generated once and committed. Regenerate them only when the receipt schema
changes — a new signature every run would make the diff noise hide a real schema change.
They are produced from `workattest.scenario.build_accepted_receipt`, chaining the second
receipt onto `compute_receipt_hash` of the first.
