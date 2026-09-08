# INVARIANTS — WorkAttest (v1)

> **Proof before acceptance.**

System invariants: properties that must **always** hold. Each one is testable and maps to
threats (`docs/THREAT-MODEL.md`) and to accountability facts
(`docs/ACCOUNTABILITY-MODEL.md`). Violating any of them invalidates the receipt.

Terminal policy states, by convention: `ACCEPT` / `HOLD` / `REFUSE`.

---

| ID | Invariant | Category | How it is tested |
|---|---|---|---|
| **INV-1** | No execution exists without a `WorkRequest`. | Authority | Reject `execution start` without a valid `request_id` |
| **INV-2** | No execution begins without a valid subject and authorization. | Identity | Reject start when subject/auth is missing or invalid |
| **INV-3** | No impactful action is accepted outside the authorized scope. | Authorization | Action outside `allowed_actions/resources` → HOLD/REFUSE |
| **INV-4** | Information declared by the agent is never verified evidence. | Integrity | Evidence only from an authorized source; a claim is not a fact |
| **INV-5** | The agent never chooses the checks that verify it. | Segregation | Checks come from operator config, not from the agent's request |
| **INV-6** | Every relevant artifact carries a hash before and/or after. | Integrity | `ArtifactEvidence` requires `before_hash`/`after_hash` |
| **INV-7** | Every `VerificationResult` identifies the exact check definition. | Verification | `definition_hash` present and bound to the check |
| **INV-8** | Absent mandatory checks never amount to approval. | Fail-safe | Missing mandatory check → HOLD, never ACCEPT |
| **INV-9** | An approval can only accept the result of the same execution. | Segregation | `approval.result_hash` == that execution's own result |
| **INV-10** | The approver's identity derives from authentication. | Identity | Approver is an authenticated subject, never a free-text name |
| **INV-11** | Actions and decisions are append-only. | Integrity | No update/delete; append only, with a hash chain |
| **INV-12** | Every receipt is serialized canonically. | Determinism | Canonicalization round-trip is stable and reproducible |
| **INV-13** | Every final receipt is signed. | Crypto | `signatures` non-empty; signing is mandatory at issuance |
| **INV-14** | Changes to the receipt or to what it covers are detectable. | Integrity | Tampering with any byte → verification fails |
| **INV-15** | Every receipt can be verified externally. | Independence | Offline verification with the public key and schema alone |
| **INV-16** | High-risk actions require human approval. | Authority | High `risk_class` without approval → HOLD |
| **INV-17** | Exceptions are explicit, justified and carried in the receipt. | Transparency | An exception without a recorded justification is invalid |
| **INV-18** | A `REFUSE` never becomes an `ACCEPT` without re-evaluation. | State | A REFUSE→ACCEPT transition requires a recorded re-evaluation |
| **INV-19** | Sensitive content is never included in evidence automatically. | Privacy | Default is hash+ref/classification; inclusion is explicit |
| **INV-20** | Identity, policy, signature or verification failures close safely. | Fail-safe | Any failure on these axes → HOLD/REFUSE, never ACCEPT |

---

## Test strategy

- **Unit tests** — every invariant has at least one positive and one negative test.
- **Property-based tests** — determinism (INV-12) and the hash chain (INV-11) validated
  against generated inputs.
- **Adversarial tests** — INV-4/5/8/9/14/18/20 map directly onto T-1…T-12 in
  `docs/THREAT-MODEL.md`.
- **Conformance suite** — checks that any verifier implementation upholds INV-12…INV-15.

> The golden rule: if an invariant has no test that fails when it is violated, the
> invariant does not exist yet.
