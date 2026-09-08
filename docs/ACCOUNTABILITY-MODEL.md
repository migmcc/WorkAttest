# ACCOUNTABILITY MODEL — WorkAttest

> **Proof before acceptance.**

Defines **what "accepted work" means** in WorkAttest: which facts are proven, with what
force, and where the system's responsibility ends. It is the conceptual contract that the
receipt makes concrete.

---

## 1. The unit of accountability

The unit is **not** the prompt, the conversation, the model call, the isolated tool call,
the log, or the agent. It is **accepted work**:

```
Authorized request
+ identity of the human and of the agent
+ permissions used
+ actions executed
+ artifacts produced or changed
+ independent verifications
+ exceptions and risks
+ authenticated approval
+ signed receipt
= Verifiable Work Receipt
```

## 2. The chain of custody (9 links)

Each link must be **cryptographically bound** to the next for the work to count as
accepted:

| # | Link | Fact proven | Cryptographic binding |
|---|---|---|---|
| 1 | Request | The work began with an identifiable `WorkRequest` | `request_id`, hash of the request |
| 2 | Identity | Human and agent are verifiable subjects | public key / signed claims |
| 3 | Authorization | Valid authority existed, with scope and validity | `authorization.signature` |
| 4 | Actions | Relevant actions were recorded by an authorized source | `ActionEvent` hash chain (`actions_root`) |
| 5 | Artifacts | The artifacts are identified | `before_hash` / `after_hash` |
| 6 | Verification | The declared checks actually ran | `VerificationResult` + `definition_hash` + `output_hash` |
| 7 | Policy | The applied policy is identified and versioned | `policy_id` + policy hash |
| 8 | Approval | The responsible person accepted *exactly* that result | `approval.result_hash` == result, plus signature |
| 9 | Receipt | The final envelope is intact and verifiable offline | `receipt_hash` + `signatures` |

Break any link and the work is **not** accepted (it closes to `HOLD`/`REFUSE`).

## 3. Evidential force (what the receipt does and does not prove)

| Proves (within the trust model) | Does **not** prove |
|---|---|
| The work began with an identifiable request | That the code is free of bugs |
| The subject held a valid authorization, with scope and validity | That an analysis is correct |
| Actions were recorded by an authorized source | That a document is legally sound |
| Artifacts are identified by hash | That the model never hallucinates |
| The declared verifications ran | That the configured checks are sufficient |
| The agent did not choose the checks | That the human approval was competent |
| The policy is identified and versioned | That the organizational policy is adequate |
| The approval binds to the exact result | |
| The approver's identity derives from authentication | |
| Later changes are detectable | |
| The receipt is checkable without trusting the app that produced it | |

**The correct promise (procedural and evidential):**
> WorkAttest proves that the defined process was followed, and binds that process to the
> accepted result.

## 4. Accountability decisions

Per evaluation, the policy emits exactly one of three terminal states:

- **ACCEPT** — valid authorization, identified artifacts, all mandatory gates passed, and
  (where required) the result was approved.
- **HOLD** — missing evidence, missing approval, a segregation-of-duties problem, or a
  mandatory check that did not run. Recoverable with new evidence or approval.
- **REFUSE** — forbidden action, invalid identity, expired authorization, policy violation,
  or evidence inconsistent with the artifact. A `REFUSE` **never** becomes an `ACCEPT`
  without a new evaluation.

## 5. Segregation of duties

- The **agent** executes; it does **not** choose or alter the checks that verify it (link 6).
- The **operator/organization** defines the mandatory checks and the policy.
- The **human approver** accepts the result; their identity **derives from authentication**,
  not from a declared name. A person **never** approves the proof of another execution.
- The **independent verifier** validates the receipt without trusting the issuing
  application.

## 6. Roles (a simplified RACI for accepted work)

| Role | Responsibility in the receipt |
|---|---|
| Owner (human) | Creates the request; owns the work |
| Agent (AI) | Executes within the authorized scope |
| Policy | Classifies risk, demands evidence/approval, decides |
| Verifier | Runs and attests the checks (independently of the agent) |
| Approver | Accepts the exact result, with an authenticated identity |
| Issuer | Issues and signs the canonical receipt |
| Independent Verifier | Confirms everything offline |

## 7. Links

- The invariants that guarantee these facts: `docs/INVARIANTS.md`.
- Where trust begins and ends: `docs/TRUST-BOUNDARIES.md`.
- Threats against each link: `docs/THREAT-MODEL.md`.
- Envelope structure: `schemas/work-receipt.schema.json`.
