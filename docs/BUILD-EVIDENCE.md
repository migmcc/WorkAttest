# BUILD EVIDENCE — MVP core (Phase 1–3)

Provenance for the execution-phase build, recorded 2026-07-16.

## Environment

- Python 3.13.14 · pytest 9.1.1 · cryptography 49.0.0 · venv at `.venv/`
- Package installed editable (`pip install -e .`)

## Test run (verified)

```text
.venv/Scripts/python -m pytest
85 passed in 7.75s
```

Covers: canonical serialization, hashing, Ed25519 sign/verify, hash-chained event log,
deterministic policy (ACCEPT/HOLD/REFUSE incl. directory-scope authorization), receipt
issue/verify, **receipt chains**, the adversarial tamper suite (`tests/adversarial/`)
mapping to THREAT-MODEL T-1, T-2, T-6 (+ policy HOLD/REFUSE cases T-5, T-7, T-8, INV-9
cross-execution rejection, INV-10 forged-approver rejection), the **verifier runner**
(`tests/unit/test_verification.py`), signed-approval tests, and **Git adapter integration
tests** (`tests/integration/`) against real temporary repos, plus salted field commitments,
receipt redaction/opening, and disclosure-tamper detection (`tests/unit/test_redaction.py`).

## Git adapter — Phase 3 (verified)

```text
workattest observe-git --repo <r> --before HEAD --allowed-prefix src/   -> ACCEPT; Receipt VALID
# after adding a file outside src/:
workattest observe-git --repo <r> --before HEAD --allowed-prefix src/   -> REFUSE (out of scope); Receipt VALID
```

The adapter observes a real repository via `git` (untracked adds, modifies, deletes),
computes before/after SHA-256 per file (INV-6), and the flow enforces directory scope:
a change outside the authorized prefix yields REFUSE (PRD §6 step 7) — recorded in a
signed, offline-verifiable receipt.

## Verifier runner — Phase 3 / TASK-302 (verified)

```text
workattest observe-git ... --checks pass.json   -> check[*] tests: passed (exit 0); ACCEPT; VALID
workattest observe-git ... --checks fail.json   -> check[*] tests: failed (exit 1); HOLD (INV-8)
```

Operator-defined checks (JSON config, trusted input — INV-5) run as subprocesses; each
result records exit code, output hash and timing. A failed/missing mandatory check forces
HOLD, never ACCEPT (INV-8).

## Authenticated human approval — core thesis (verified)

```text
observe-git ... --high-risk                        -> HOLD (approval missing, INV-9/INV-16)
observe-git ... --high-risk --approver-key a.pem   -> ACCEPT; Receipt VALID
receipt verify a.json                              -> 7/7 PASS incl. "approval signatures valid"
```

An approval is signed by the approver's Ed25519 key, binds to the execution id + result
hash (INV-9), and the verifier confirms the signature AND that the signing key matches the
approver subject registered in the receipt (INV-10). Adversarial test: a validly-signed but
wrong-key approval, with the whole receipt re-signed, is still rejected by the identity check.

## Receipt chains — Phase 2 (verified)

```text
receipt verify-chain r0.json r1.json r2.json           -> Chain VALID (3 receipts); exit 0
receipt verify-chain r0.json r2.json r1.json (reorder)  -> Chain INVALID; exit 1
```

Each non-root receipt's `previous_receipt_hash` commits to its predecessor's
`receipt_hash`. Reordering, inserting, deleting, or tampering any receipt breaks a link.
A chain is valid only if every receipt is individually valid and every link matches.

## Redaction — salted field commitments (verified)

```text
.venv/Scripts/python -m workattest.cli receipt open receipt.json reviewer_note
  -> disclosure opened successfully; exit 0
.venv/Scripts/python -m workattest.cli receipt redact receipt.json --field reviewer_note --out redacted.json
  -> Receipt VALID; exit 0
.venv/Scripts/python -m workattest.cli receipt verify redacted.json
  -> Receipt VALID; exit 0
.venv/Scripts/python -m workattest.cli receipt open redacted.json reviewer_note
  -> Redacted: field 'reviewer_note' is redacted (commitment only); exit 1
```

Design: a sensitive field is committed as `sha256(canonical{salt,value})` in the *signed*
payload (`commitments`) and disclosed in an *unsigned* `disclosures` sidecar. Redacting
drops the disclosure — `receipt_hash` and signatures are unchanged — so the receipt still
verifies while the value is withheld (INV-19); a tampered disclosure fails the
"disclosures match commitments" check. The CLI smoke test explicitly confirmed the
redacted receipt kept the original `receipt_hash` and signatures byte-for-byte while
removing the disclosure. CLI: `receipt redact` / `receipt open`.

## What this proves (against docs/PRD.md §7 DoD)

Implemented and green: receipt schema v1, Ed25519 signatures, deterministic policy,
independent offline verifier, approval bound to execution id + result hash and signed by
the approver, tamper detection, Git evidence capture, operator check execution, receipt
chains, and redaction. **Not yet:** richer identity (OIDC/SSO), transparency log
(Phase 6+ — see TASKS.md).

## Scope boundary

No product code beyond the MVP core was written. At the time this evidence was recorded, the
human gates (`pp final-validation`, `pp done`) remained unapproved and were left to the human
owner.

> **Addendum (2026-09-07).** Those gates were closed later the same day and are recorded in
> `.project-pilot/status.json`: `final_validation_prepared` at `2026-07-16T07:10:25Z` and
> `done_approval` at `2026-07-16T08:55:50Z` — reason *"MVP core verified: 85 tests passing,
> redaction CLI smoke green, artifact hashes current, and Git baseline clean"*, source `manual`.
> The lifecycle phase is `done`. The paragraph above is kept as originally recorded rather than
> rewritten: this is a provenance document, and amending it in place would defeat its purpose.
