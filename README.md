# WorkAttest

> **Proof before acceptance.**

Local-first, verifiable infrastructure that cryptographically links **request →
identity → authorization → execution → evidence → verification → human approval** to a
signed, **offline-verifiable receipt** for AI-assisted work.

WorkAttest does not try to prove that an AI never errs. It proves that **no relevant
work is accepted without authority, evidence, validation and identifiable
responsibility** — and ties that proof to the exact artifact.

- Product vision & scope: [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md), [`docs/PRD.md`](docs/PRD.md)
- Requirements & plan: [`docs/PRD.md`](docs/PRD.md), [`docs/ROADMAP.md`](docs/ROADMAP.md)
- Trust model: [`docs/ACCOUNTABILITY-MODEL.md`](docs/ACCOUNTABILITY-MODEL.md), [`docs/TRUST-BOUNDARIES.md`](docs/TRUST-BOUNDARIES.md), [`docs/THREAT-MODEL.md`](docs/THREAT-MODEL.md), [`docs/INVARIANTS.md`](docs/INVARIANTS.md)
- Receipt contract: [`schemas/work-receipt.schema.json`](schemas/work-receipt.schema.json)

## Status

Early MVP core (Phase 1 + the crypto receipt heart of Phase 2). Implemented:

- Canonical JSON serialization (RFC 8785 subset) — deterministic hashing.
- SHA-256 content hashing (`HashRef`).
- Ed25519 keys + detached signatures (offline-verifiable).
- Append-only, hash-chained action event log (tamper-evident).
- Deterministic policy engine → `ACCEPT` / `HOLD` / `REFUSE`.
- Receipt issuer + **offline verifier** with adversarial tamper tests.
- **Git adapter** — observe a real repository (adds/modifies/deletes), hash files
  before/after, enforce directory scope, and issue a receipt for an actual change.
- **Verifier runner** — execute operator-defined checks (from a trusted JSON config) as
  subprocesses and attest their real exit code, output hash and timing; a failed/missing
  mandatory check forces HOLD (INV-8). The agent never chooses these checks (INV-5).
- **Authenticated human approval** — a high-risk change reaches ACCEPT only with an
  Ed25519-signed approval bound to the exact result; the verifier confirms the signature
  and that it came from the registered approver (INV-9, INV-10).
- **Receipt chains** — receipts link to their predecessor (`previous_receipt_hash`);
  reordering, inserting, or tampering any receipt breaks the chain.
- **Redaction** — sensitive fields are committed (salted hash) in the *signed* payload and
  disclosed in an *unsigned* sidecar; you can drop the disclosure and the receipt still
  verifies, while a revealed value is checked against its commitment (INV-19).
- Minimal CLI (`init`, `keygen`, `demo`, `observe-git`, `receipt verify | verify-chain | redact | open`).

Not yet built: transparency log, richer identity (OIDC/SSO). See the roadmap and `TASKS.md`.

## Install (development)

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"   # Windows
# source .venv/bin/activate && pip install -e ".[dev]"   # POSIX
```

## Try it

```bash
# Build a signed demo receipt for an AI-assisted change and verify it offline
workattest demo --out receipt.json

# Verify a receipt on ANY machine, using only the public key inside it
workattest receipt verify receipt.json

# Observe a REAL git change and issue a receipt (scope-enforced)
workattest observe-git --repo /path/to/repo --before HEAD --allowed-prefix src/
# A change outside src/ produces a REFUSE receipt (still signed and verifiable).
```

`receipt verify` exits `0` when the receipt is valid and `1` when tampering is detected.

You can try this without issuing anything — the repository ships receipts signed elsewhere:

```bash
workattest receipt verify tests/vectors/receipt-accepted-v1.json
```

## Run the tests

```bash
.venv/Scripts/python -m pytest
```

The suite includes adversarial tests (`tests/adversarial/`) proving that flipping a
field, swapping an artifact hash, stripping/forging a signature, reusing an approval
across executions, substituting a weaker policy, declaring a check that never ran, or
relabelling a REFUSE as ACCEPT all make verification fail. All twelve threats in
`docs/THREAT-MODEL.md` §4 (T-1…T-12) are covered, and §4 maps each one to its test.

`tests/vectors/` holds signed receipts that the test suite never issues — they were
produced once, on another machine, by keys that no longer exist. CI verifies them on
Linux, macOS and Windows, which is what makes "verifiable on any machine" a tested
property rather than a claim. See [`tests/vectors/README.md`](tests/vectors/README.md).

## The promise (and its limits)

WorkAttest's promise is **procedural and probatory**: it proves the defined process was
followed and links it to the accepted result. It does **not** claim the code is bug-free,
that a model never hallucinates, or that a human approval was competent. See
[`docs/ACCOUNTABILITY-MODEL.md`](docs/ACCOUNTABILITY-MODEL.md) §3.

## License

MIT. See [`LICENSE`](LICENSE).
