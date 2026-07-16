# Security Policy

WorkAttest is security- and cryptography-critical software. Its value depends entirely
on the integrity of its trust model.

## Reporting a vulnerability

Please report suspected vulnerabilities privately (do not open a public issue). Include a
description, reproduction steps, and impact. We aim to acknowledge within a few business
days. Coordinated disclosure is appreciated.

## Trust model & scope

Read these before reasoning about security guarantees:

- [`docs/TRUST-BOUNDARIES.md`](docs/TRUST-BOUNDARIES.md) — trust anchors and zones.
- [`docs/THREAT-MODEL.md`](docs/THREAT-MODEL.md) — adversaries, STRIDE per link, and the
  adversarial tests (T-1…T-12) that must fail the receipt when an attack is attempted.
- [`docs/INVARIANTS.md`](docs/INVARIANTS.md) — the 20 invariants the code must uphold.

## Key handling (MVP)

- Signing uses **Ed25519**. The MVP stores private keys as **unencrypted PKCS#8 PEM** on
  the local filesystem — this is acceptable only for development and demos.
- **Do not** use MVP key storage for production. Enterprise deployments must use an HSM,
  a KMS, or keyless signing (Sigstore). See [`docs/STANDARDS-DECISIONS.md`](docs/STANDARDS-DECISIONS.md).
- If a signing key is compromised, forged receipts become possible — this is an accepted,
  documented residual risk of the MVP (THREAT-MODEL §5). Mitigate with short-lived,
  rotated keys.

## Check execution (verifier runner)

The verifier runner executes the `command` of each configured check as a subprocess.
Check definitions are therefore **trusted operator input** and must never be sourced from
the agent under evaluation or from an untrusted repository (INV-5). Runs are bounded by a
per-check timeout. Do not point the runner at check configs you do not control.

## Known residual risks (MVP)

- **Weak timestamps** — timestamps use the local clock and are not strong proof of time.
  Future: RFC 3161 TSA / transparency log.
- **Observer host integrity** — evidence collection assumes the observing host is intact.

## Fail-safe principle

Any failure of identity, policy, signature, or verification must close to `HOLD`/`REFUSE`,
never `ACCEPT` (INV-20). Report any path that violates this as a security bug.
