# Task Routing — WorkAttest

Generated: 2026-07-15. Routes tasks to the active team (see `TEAM.md`) based on the
languages, tools, and constraints declared in `INIT.md`.

## Routing table

| Task signal | Route to | Notes |
|---|---|---|
| Any `.py` change | **python-reviewer** → **code-reviewer** | Python is the only language |
| Crypto, signing, hashing, key handling | **security-reviewer** (mandatory) | Core, security-critical (INV-13/14/15) |
| Identity, authorization, policy engine | **security-reviewer** + **code-reviewer** | Fail-safe + segregation of duties |
| Receipt schema / canonical serialization | **architect** → **api-contract-first** skill | Contract-first; INV-12 |
| Evidence handling, redaction, classification | **compliance-reviewer** | GDPR/RGPD data minimization (INV-19) |
| New domain entity / state machine | **architect** (ADR) → **python-reviewer** | Keep domain infra-independent |
| New feature / capability | **brainstorming** → **writing-plans** → **tdd-guide** | RED before GREEN |
| Any bug / test failure / unexpected behavior | **debugger** (root cause first) | Iron Law — no fix before root cause |
| Build or type error | **build-error-resolver** | Minimal diffs only |
| Dead code / duplication | **refactor-cleaner** | Only your own orphans |
| Docs / codemaps after a feature lands | **doc-updater** | Contracts-first project |
| Adversarial / property-based tests | **tdd-guide** + **security-reviewer** | Maps to THREAT-MODEL T-1…T-12 |
| Before any PR merge | **code-reviewer** + **security-reviewer** (quality-gate) | |
| Pipeline compliance audit | **harness-optimizer** | Verify skills actually ran |

## Mandatory gates (from INIT.md specialConstraints)

- Any change to **crypto / identity / policy / receipt** → **security-reviewer** is required.
- Verification claims ("tests pass", "build succeeds", "done") → **verification-before-completion**.
- Human approval gates (execution, final-validation, done) stay **explicit** — never auto-approved.
- No absolute-guarantee claims in code, docs, or output.

## File Claims

| File | Agent | Task | Status |
|------|-------|------|--------|
| (empty — populated at dispatch time) | | | |
