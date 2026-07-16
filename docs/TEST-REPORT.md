# TEST REPORT — WorkAttest MVP

Date: 2026-07-16  
Lifecycle phase at execution: `final-validation`

## Environment

- Python 3.13.14
- pytest 9.1.1
- cryptography 49.0.0
- package installed editable from this workspace

## Full automated suite

Command:

```text
.venv/Scripts/python -m pytest
```

Observed result: `85 passed`; exit code `0`; zero failures.

Coverage includes canonical serialization, hashing, Ed25519 signing and verification,
hash-chained events, deterministic policy decisions, signed approvals, receipt issue and
offline verification, receipt chains, Git adapter integration, operator-defined checks,
adversarial tampering, salted commitments, redaction, and disclosure integrity.

## Redaction CLI smoke test

The public CLI was exercised end to end:

1. create a signed demo receipt;
2. open `reviewer_note` before redaction — exit `0`;
3. redact `reviewer_note` — redacted receipt `VALID`, exit `0`;
4. verify the redacted receipt independently — `VALID`, exit `0`;
5. open `reviewer_note` after redaction — documented redacted result, exit `1`.

Explicit assertions passed: the disclosure was removed while `receipt_hash` and signatures
remained unchanged.

## Result

The implemented WorkAttest MVP core is verified for the tested local environment.

## Explicit exclusions

This report does not claim completed market interviews, full T-1…T-12 adversarial coverage,
verification on a second machine, OIDC/SSO identity, a transparency log, or general proof of
the correctness of AI-produced work.
