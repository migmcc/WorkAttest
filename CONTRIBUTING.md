# Contributing to WorkAttest

WorkAttest is a trust product. Contributions are held to a high bar: **every invariant
needs a test, and security-relevant changes need a security review.**

## Ground rules

1. **Invariants first.** If you change behavior touching `docs/INVARIANTS.md`, update the
   invariant and its test in the same change. An invariant without a test that fails when
   it's violated does not exist.
2. **Determinism.** The core must stay deterministic and infrastructure-independent (no
   network, no clock-dependent logic in decisions). Floats are forbidden in canonical
   payloads — see `src/workattest/canonical.py`.
3. **Fail-safe.** Any failure of identity, policy, signature, or verification must resolve
   to `HOLD`/`REFUSE`, never `ACCEPT` (INV-20).
4. **No absolute-guarantee claims** in code, docs, comments, or output.

## Workflow

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"
.venv/Scripts/python -m pytest      # must be green before you push
```

- Keep changes surgical — scoped to the task.
- Add adversarial tests for any new trust-relevant path (map them to THREAT-MODEL T-IDs).
- Human-approval and release gates stay explicit; automation never self-approves.

## Tests layout

- `tests/unit/` — canonical, hashing, crypto, events, policy, receipts.
- `tests/adversarial/` — tamper/cross-execution attacks that must fail verification.
- `tests/vectors/` — signed receipts verified without the issuer; see the README there
  before regenerating them.

## Licensing of contributions

By contributing, you agree that your contributions are licensed under the project's
[MIT License](LICENSE).
