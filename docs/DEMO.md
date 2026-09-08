# Demo — AI software change → signed receipt → offline verify

This walkthrough exercises the MVP core end-to-end. It mirrors the acceptance scenario in
[`docs/PRD.md`](PRD.md) §6, in code you can run today.

## 1. Build a signed receipt

```bash
workattest demo --out receipt.json
```

The `demo` command (see `src/workattest/scenario.py`) constructs a full accepted-work case:

- a **WorkRequest** ("fix a null-pointer in the auth handler"), classified **high risk**;
- an **Authorization** scoped to `src/auth/login.py`, expiring 2026-12-31, requiring approval;
- an **ExecutionSession** by an agent subject, owned by a human;
- an append-only, **hash-chained action log** (`edit_file`, `run_check`);
- **ArtifactEvidence** with before/after hashes;
- two **mandatory** verification checks (`tests`, `lint`), both passed;
- a **human ApprovalDecision** bound to the exact result hash of this execution;
- a deterministic policy evaluation → **ACCEPT**;
- an **Ed25519 signature** over the canonical payload.

Expected output ends with:

```
Receipt VALID
PASS  schema_version supported
PASS  required fields present
PASS  receipt_hash matches payload
PASS  at least one valid signature
PASS  approvals bind to this execution/result
PASS  ACCEPT has required approval
```

## 2. Verify on another machine

Copy only `receipt.json` to any machine with WorkAttest installed — no server, no network,
no access to the issuer:

```bash
workattest receipt verify receipt.json   # exit 0 = valid
```

Verification uses **only** the public key embedded in the receipt's signature (INV-15).

## 3. Prove tampering is caught

Any of these break verification (exit 1):

- edit any covered field (e.g. `request.intent`) → `receipt_hash matches payload` FAILS (T-1);
- change an artifact's `after_hash` → FAILS (T-2);
- empty or forge `signatures` → `at least one valid signature` FAILS (INV-13);
- point an approval at a different `execution_id` → `approvals bind…` FAILS (T-6 / INV-9).

These are encoded as automated tests in [`tests/adversarial/test_tamper.py`](../tests/adversarial/test_tamper.py).

## What this demonstrates

The six MVP success criteria from `docs/PRD.md` §7, minus the Git adapter (Phase 3): a
third party, given only the receipt and the public key, can confirm the work was
authorized, verified, approved for that exact result, and unaltered.
