# PROJECT BRIEF — WorkAttest

> **Proof before acceptance.**

| | |
|---|---|
| **Project** | WorkAttest (`workattest`) |
| **Category** | Verifiable Work Accountability |
| **First market** | Software changes produced or assisted by AI agents |
| **Status** | MVP core built and tested. Market validation deliberately not pursued — see the addendum in §12 |

---

## 1. Problem

Agents such as Claude Code, Codex and Cursor produce code, decisions and actions at high
speed. Logs, traces and chat histories help reconstruct what happened, but they **do not
constitute a verifiable chain of custody, nor a formal acceptance of the result**. In most
current workflows it remains hard to prove who started the work, what authority existed,
which actions and artifacts resulted, which verifications actually ran, and who approved
the *exact* result.

## 2. Thesis

The unit of accountability is not the prompt, the conversation, the tool call, the log or
the agent — it is **accepted work**. Accepted work cryptographically binds:

```
authorized request + identity (human + agent) + permissions used
+ actions executed + artifacts changed + independent verifications
+ exceptions/risks + authenticated approval + signed receipt
= Verifiable Work Receipt
```

The promise is **procedural and evidential**, not one of correctness:

> WorkAttest proves that the defined process was followed and binds that process to the
> accepted result. It does not guarantee that the code is free of bugs, that a model never
> hallucinates, or that a human approval was competent.

This honesty about scope is deliberate, and it is what makes the receipt defensible to
auditors and lawyers.

## 3. First wedge — AI Software Change Accountability

Control the lifecycle of an AI-assisted software change, demonstrable on a pull request:

`WorkRequest` → identity + policy → authorization (`ACCEPT/HOLD/REFUSE`) → observed
execution → Git snapshots + actions → Verifier (operator-defined checks) → authenticated
human approval (high risk) → **signed Verifiable Work Receipt** → independent offline
verification → status check on GitHub/GitLab.

## 4. Target customer (initial ICP)

Engineering teams of 20–300 people who already use coding agents, produce software with
financial, operational or regulatory impact, have CI, pull requests and approvals, and need
to **demonstrate** how a change was produced and accepted — without replacing GitHub,
GitLab, Jira or the agents they already use. Priority sectors: fintech, banking, insurance,
health tech, automotive, industrial, legal tech, cybersecurity, regulated B2B.

## 5. Differentiation

WorkAttest is **not** an editor, an agent, an agent framework, observability, a SIEM,
generic GRC, a project manager or an IAM. It is a **neutral layer** between those systems.

Other tools prove that an agent called a tool, that a user started a session, that a policy
allowed an action, or that a commit passed CI. WorkAttest **additionally** proves that the
commit corresponds to the authorized request, that the concrete artifacts are identified,
that the applicable checks ran, that the evidence belongs to that version, that no
obligation was skipped, and that the responsible person accepted *exactly* that result —
verifiable outside WorkAttest.

## 6. Technical strategy

- **A deterministic core, independent of infrastructure** (no dependency on FastAPI,
  GitHub, Claude, Codex or a particular database): entities, states, invariants, decisions,
  canonical serialization.
- **Standards first** — avoid proprietary cryptography: in-toto, DSSE, Sigstore/Rekor,
  SCITT, OIDC, SPIFFE/SPIRE, SLSA, SBOM, Git signing, GitHub attestations.
- **Disciplined reuse** — ProjectPilot, Taevdar and Agent Trust Gate as customers or
  component donors, **not** as the core. Do not inherit the anti-pattern of "editable JSON
  state as final proof".

## 7. MVP scope

**Goal:** demonstrate that a software change can be authorized, observed, verified,
approved and turned into a receipt that validates **offline**.

**Includes:** receipt schema v1 · Ed25519 signatures · Git adapter · filesystem evidence ·
a deterministic policy with `ACCEPT/HOLD/REFUSE` · an independent verifier · approval bound
to the execution ID · offline verification · adversarial tamper tests · a documented threat
model · a Claude/Codex → Git → receipt demo.

**Minimal CLI:** `workattest init | request create | policy evaluate | execution
start/observe | evidence add | verify run | approve | receipt issue | receipt verify`.

**Outside the MVP:** dashboard/PWA · multi-tenant SaaS · billing · a complete GitHub App ·
extensive EU AI Act/ISO compliance · SIEM/ServiceNow · a bespoke blockchain · a custom LLM
· an agent framework. *The MVP proves the accountability model, not the breadth of a
platform.*

## 8. Key invariants (v1)

No execution without a `WorkRequest` and a valid authorization · information declared by
the agent is never verified evidence · the agent never chooses the checks that verify it ·
absent mandatory checks are not an approval · an approval only accepts the result of the
same execution · actions and decisions are append-only · every receipt is canonical, signed
and externally verifiable · changes to evidence are detectable · identity, policy,
signature and verification failures close safely. *(The full list is in
`docs/INVARIANTS.md`.)*

## 9. Success criteria (MVP)

An outside person, given the artifact, the receipt, the key or identity chain, and the
evidence references, can independently confirm: (1) this was the authorized work; (2) that
execution produced the artifact; (3) the applicable checks ran; (4) the result matches the
hashes; (5) the responsible person approved exactly that result; (6) the receipt was not
altered.

**Primary metric:** *accepted work receipts per team per week* (counted only with a final
artifact, checks run, policy evaluated, approval obtained and a valid signature).
**Guardrails that must stay at zero:** cross-execution proof mismatch, unsigned final
receipts, unauthorized impact accepted, mandatory checks skipped, undetected integrity
failures.

## 10. Risks and stop criteria

| Risk | Severity | Mitigation |
|---|---|---|
| **Willingness-to-pay unproven** | **Existential** | Sell risk reduction; demonstrate incident reconstruction; find design partners with concrete pain |
| Category too broad / cost of educating the market | High | Start with software changes only; demo on a pull request; avoid "AI governance" claims |
| Standards and vendors (GitHub Attestations, Sigstore, SLSA) move into the lane | High | Integrate standards rather than compete; differentiate on *accepted work* plus human approval bound to the exact artifact |
| The Execution Gateway (observing without trusting the agent) is the hardest, most intrusive piece | Medium-High | The MVP limits itself to Git snapshots and observed commands; avoid scope creep |
| A receipt with no legal or audit value | Medium | Involve auditors and lawyers early; document the limits; map evidence |
| Logging creates new risks | Medium | Minimization, redaction, encryption, evidence references, configurable retention |

**Stop if:** there is no willingness to pay · receipts do not change procurement, audit or
release decisions · the integrations required make the product unviable · competitors offer
a complete, accessible flow before validation.

## 11. Roadmap (macro)

Phase 0 discovery and contracts → Phase 1 deterministic core → Phase 2 cryptographic
receipts → Phase 3 software change adapter (Git) → Phase 4 ProjectPilot integration →
Phase 5 Taevdar control plane → Phase 6 GitHub App → Phase 7 enterprise control plane.
Detail in `docs/ROADMAP.md`.

## 12. Validation decision (recorded)

**APPROVED (conditional)** — source: manual, via ProjectPilot.

A sound thesis (the unit of accountability is accepted work); an MVP that is technically
feasible and well bounded; an honest scope (procedural and evidential, not correctness).
**The dominant risk is market risk, not build risk.**

**Binding condition:** run the market validation interviews **in parallel** with Phases
0 and 1, and treat willingness-to-pay as the primary stop criterion. This approval covers
**building the MVP core and validating demand** — not building the full enterprise
platform. Tracked as TASK-004 in `TASKS.md`.

> **Addendum (2026-09-09) — the binding condition was not met, by decision.**
>
> The market validation interviews were never started and are not going to be. The purpose
> of the project changed: WorkAttest is published as a technical artifact — a demonstration
> of the accountability model and of how it is verified — rather than as a venture looking
> for customers.
>
> What follows, stated plainly so no reader has to infer it:
>
> - The commercial thesis in this brief (§4 ICP, §10 risks) is **unvalidated**. Nobody has
>   been asked whether they would pay for this.
> - "The dominant risk is market risk, not build risk" remains true, and remains untested.
> - Phases 4-7 of `docs/ROADMAP.md` are **not being executed**. They record a direction that
>   was considered, not work in progress.
> - The MVP core, its invariants and its adversarial coverage are complete and tested. They
>   stand on their own terms, which is what this repository is for.
>
> The original decision above is kept as recorded rather than edited. It was the right call
> on the information available in July; what changed afterwards was the goal, not the
> reasoning.

## 13. Next sequence of work

1. Advance through the ProjectPilot lifecycle (setup-advice → execution).
2. Produce the Phase 0 contracts: `ACCOUNTABILITY-MODEL.md`, `THREAT-MODEL.md`,
   `TRUST-BOUNDARIES.md`, `INVARIANTS.md`, `schemas/work-receipt.schema.json`,
   `COMPETITIVE-MATRIX.md`, `STANDARDS-DECISIONS.md`.
3. Start the market interviews in parallel.
4. Phase 0 gate: trust model reviewed · receipt v1 approved · first use case closed · zero
   "absolute guarantee" claims.
