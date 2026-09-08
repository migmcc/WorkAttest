# PRD — WorkAttest (MVP: AI Software Change Accountability)

> **Proof before acceptance.**

| | |
|---|---|
| **Document** | Product Requirements Document |
| **Scope** | MVP — the first wedge (AI-assisted software changes) |
| **Status** | MVP core built (see `TASKS.md` for what remains open) |
| **Source** | `PROJECT_BRIEF.md` |
| **Out of scope** | See §9 and `PROJECT_BRIEF.md` §7 |

---

## 1. Product goal (MVP)

Demonstrate, end to end, that an AI-assisted software change can be **authorized,
observed, verified, approved and turned into a signed receipt that any third party can
validate offline** — without trusting the application that produced it.

The MVP proves the **accountability model**, not the breadth of a platform.

## 2. Users and jobs to be done

| User | Job | Need the MVP meets |
|---|---|---|
| Developer / agent operator | Run an AI-assisted change | Get scoped authorization and produce evidence without manual friction |
| Engineering manager / approver | Accept a result | Approve *exactly* the verified artifact, with an authenticated identity |
| Security / quality engineer | Define and enforce checks | Ensure mandatory checks run and that the agent does not choose them |
| Auditor / compliance | Reconstruct and trust | Verify offline that the process was followed and bound to the artifact |
| External third party | Trust without server access | Validate a receipt with a public key, without WorkAttest |

## 3. Functional requirements

### 3.1 WorkRequest and authorization
- **FR-1** The system records a `WorkRequest` (intent, scope, owner, system, risk_class, acceptance_criteria).
- **FR-2** The policy evaluates the request and emits `ACCEPT` / `HOLD` / `REFUSE` **deterministically**.
- **FR-3** A valid authorization defines the subject, allowed actions, resources, conditions, validity and whether approval is required. No impactful action is accepted outside the authorized scope.

### 3.2 Identity
- **FR-4** Every subject (human, agent, service account) is verifiable by key (MVP: local Ed25519, Git/GitHub identity, OIDC in CI). Identity is **never** merely a name in the request body.

### 3.3 Execution and observation
- **FR-5** An `ExecutionSession` binds request, authorization, agent, human, model and workspace.
- **FR-6** The Git adapter captures the initial and final state (commits, diffs, file hashes).
- **FR-7** Relevant `ActionEvent`s are recorded append-only with a chained hash (`previous_event_hash`). Information declared by the agent is **never** treated as verified evidence.

### 3.4 Evidence and verification
- **FR-8** `ArtifactEvidence` records before/after hash, media type, size, source and classification for every relevant artifact.
- **FR-9** The Verifier runs **operator-defined** checks (tests, lint, typecheck, security, custom). Each `VerificationResult` records check_id, version, definition_hash, exit_code, output_hash, timing and evidence_refs.
- **FR-10** The agent does **not** choose or alter the checks that verify it. Absent mandatory checks **never** amount to approval.

### 3.5 Approval
- **FR-11** High-risk actions require an `ApprovalDecision` from an authenticated human, bound to the `result_hash` of the **same** execution, with justification and signature. Append-only.

### 3.6 Receipt and independent verification
- **FR-12** The Receipt Issuer produces a `WorkReceipt` with **canonical** serialization, a versioned schema and an Ed25519 signature, including or referencing policy, actions_root, artifacts, verification and approvals.
- **FR-13** `workattest receipt verify <file>` validates schema, signature, signer, hashes, artifacts, policy, the relationship to the execution, and approvals — **offline**, with no access to the main server.
- **FR-14** Any later change to the receipt or to the evidence it covers is **detectable**.

### 3.7 Minimal CLI
- **FR-15** `workattest init | request create | policy evaluate | execution start/observe | evidence add | verify run | approve | receipt issue | receipt verify`.

## 4. Non-functional requirements

- **NFR-1 Determinism** — the policy and canonical serialization produce the same output for the same input; receipts are hashable and reproducible.
- **NFR-2 Infrastructure independence** — the core domain does not depend on FastAPI, GitHub, Claude, Codex or any particular database.
- **NFR-3 Fail-safe** — identity, policy, signature or verification failures close safely (never as `ACCEPT`).
- **NFR-4 Append-only** — actions, decisions and approvals are not mutable.
- **NFR-5 Data minimization** — sensitive content is never included in evidence automatically; hash+reference, classification and redaction are supported.
- **NFR-6 Standards first** — prefer in-toto/DSSE/Sigstore/SCITT/SLSA over proprietary cryptography.
- **NFR-7 Offline verification** — the independent verifier requires neither the main server nor a network.

## 5. Domain model (summary)

`WorkRequest` · `Subject` · `Authorization` · `ExecutionSession` · `ActionEvent` ·
`ArtifactEvidence` · `VerificationResult` · `ApprovalDecision` · `WorkReceipt`.
Field-level detail lives in `schemas/work-receipt.schema.json` and
`src/workattest/domain/entities.py`; the invariants are in `docs/INVARIANTS.md`.

## 6. Demonstration flow (MVP acceptance)

1. A clean Git repository; the request: fix a specific bug.
2. The policy allows changes **only** in certain directories.
3. Claude Code or Codex does the work in an observed workspace.
4. WorkAttest collects the initial commit, the diff, the files, the observed commands and the final commit.
5. The Verifier runs tests, lint, typecheck, a security check and a custom check.
6. A change **outside the scope** produces `HOLD` or `REFUSE`.
7. An authenticated human approves the final commit.
8. WorkAttest issues a signed receipt.
9. **Another computer** validates the receipt with the public key.

## 7. Acceptance criteria (Definition of Done — MVP)

- [x] Receipt schema v1 published (`schemas/work-receipt.schema.json`).
- [x] Working Ed25519 signatures (sign and verify).
- [x] Git adapter (snapshots, diffs, hashes).
- [x] Filesystem evidence.
- [x] Deterministic policy with `ACCEPT/HOLD/REFUSE`.
- [x] Independent verifier; the agent does not choose the checks.
- [x] Approval bound to the execution ID and the result_hash.
- [x] Receipt verifiable **offline on another machine** — proven continuously by the
      conformance vectors in `tests/vectors/`, verified in CI on Linux, macOS and Windows.
- [x] Adversarial tests (tampering with the receipt and with evidence is detected) —
      all of T-1…T-12, mapped in `docs/THREAT-MODEL.md` §4.
- [x] Threat model documented (`docs/THREAT-MODEL.md`).
- [ ] Full Claude/Codex → Git → receipt demo. The pieces exist and are tested
      (`docs/DEMO.md`, `workattest observe-git`), but driving the chain from a live agent
      session is still done by hand.

## 8. Metrics and guardrails

**Primary metric:** *accepted work receipts per team per week* (counted only with a final
artifact, checks run, policy evaluated, approval obtained and a valid signature).

**Guardrails that must stay at zero:** receipt verification success below 100% ·
cross-execution proof mismatch · unsigned final receipts · unauthorized impact accepted ·
mandatory checks skipped · undetected evidence integrity failures.

## 9. Out of scope (MVP)

Dashboard/PWA · multi-tenant SaaS · billing · a complete GitHub App · model routing ·
memory · quotas · extensive EU AI Act/ISO compliance · SIEM/ServiceNow · a bespoke
blockchain · a custom LLM · an agent framework · an enterprise control plane
(SSO/RBAC/SoD).

## 10. Dependencies and risks (links)

- Risks and stop criteria: `PROJECT_BRIEF.md` §10.
- **Binding approval condition:** market interviews running in parallel;
  willingness-to-pay is the primary stop criterion. See `TASKS.md` TASK-004.
- Standards decisions: `docs/STANDARDS-DECISIONS.md`.
- Trust boundaries and threats: `docs/TRUST-BOUNDARIES.md`, `docs/THREAT-MODEL.md`.
