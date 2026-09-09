# ROADMAP — WorkAttest

> **Proof before acceptance.**

A macro roadmap by phase. The MVP is Phases 0–3. Phases 4 and beyond are platform
expansion and are only justified after market validation (see the stop criteria in
`PROJECT_BRIEF.md` §10).

**The golden rule:** *contracts before integrations; core before UI; a single use case
before breadth.*

---

## Timeline (macro)

```
Phase 0 ─ Phase 1 ─ Phase 2 ─ Phase 3 ─┐  (MVP)
Discovery  Determ.   Crypto    SW change │
contracts  core      receipts  adapter   │
                                         ▼
                          [ MVP gate + market validation ]
                                         │
Phase 4 ─ Phase 5 ─ Phase 6 ─ Phase 7    ▼  (expansion, only if willingness-to-pay is proven)
PPilot     Taevdar   GitHub    Enterprise
integr.    ctrl plane  App      control plane
```

**Mandatory parallel track (approval condition):** market interviews, running from Phase 0
onwards. Willingness-to-pay is the primary stop criterion.

> **This track was not run.** It was dropped by decision on 2026-09-09, when the goal changed
> from taking the product to market to publishing it as a technical artifact. Everything from
> the MVP gate rightwards in the diagram above is therefore **not in progress** — it records a
> direction that was considered. See `PROJECT_BRIEF.md` §12 and `TASKS.md` TASK-004.

---

## Phase 0 — Discovery and contracts  *(MVP)*

Formalize the model before writing core code.

**Deliverables**
- [x] `PROJECT_BRIEF.md`
- [x] `docs/PRD.md`
- [x] `docs/ROADMAP.md`
- [x] `docs/ACCOUNTABILITY-MODEL.md`
- [x] `docs/THREAT-MODEL.md`
- [x] `docs/TRUST-BOUNDARIES.md`
- [x] `docs/INVARIANTS.md`
- [x] `docs/STANDARDS-DECISIONS.md`
- [x] `docs/COMPETITIVE-MATRIX.md`
- [x] `schemas/work-receipt.schema.json` (receipt v1)

**Gate:** trust model reviewed · receipt v1 approved · first use case closed · zero
"absolute guarantee" claims · at least 3 market interviews started (this last one was not
done — see the note above).

## Phase 1 — Deterministic core  *(MVP)*

**Deliverables:** domain entities and states · canonical JSON · deterministic policy
decisions (`ACCEPT/HOLD/REFUSE`) · storage interfaces · append-only events with a hash
chain · unit tests · property-based tests · minimal CLI skeleton.

**Gate:** domain independent of infrastructure · deterministic policy under test ·
reproducible canonical serialization · domain invariants covered.

## Phase 2 — Cryptographic receipts  *(MVP)*

**Deliverables:** Ed25519 key generation and management · signing and verification · a key
rotation model · receipt chains (`previous_receipt_hash`) · redaction · an **offline
verifier** · adversarial tamper tests.

**Gate:** receipt signed and verifiable offline · tampering with receipt or evidence
detected · multiple signatures supported · schema versioned.

## Phase 3 — Software change adapter  *(MVP — closes the MVP)*

**Deliverables:** Git snapshots (initial/final) · diffs · artifact hashes · command
observation · a Verifier running operator-defined checks · human approval · a **complete
demo** from Claude/Codex through Git to a receipt.

**Gate = the MVP Definition of Done** (see `docs/PRD.md` §7). Run the demo in PRD §6 and
validate the receipt on another machine.

---

### ▲ Post-MVP decision point (`PROJECT_BRIEF.md` §10)
Continue, redirect or stop, based on: receipt validatable offline · working Git
integration · at least 2 agents supported · demonstrable policy blocks · at least 3 design
partners · at least 1 paid pilot or LOI · auditors finding the evidence useful.

---

## Phase 4 — ProjectPilot integration  *(expansion)*

ProjectPilot becomes the first lifecycle customer. Relevant transitions
(validation→brief, planning→execution, execution→final-validation, →done) may require a
valid WorkAttest receipt.

## Phase 5 — Taevdar integration  *(expansion)*

Taevdar becomes the control plane and operational experience (pending decisions,
executions, proofs, incidents, integrity, approvals, receipts). Taevdar's internal proof is
progressively replaced by WorkAttest receipts.

## Phase 6 — GitHub App  *(expansion)*

Required status checks · PR receipts · organization policies · release receipts · identity
via GitHub/OIDC · evidence links · branch protection.

## Phase 7 — Enterprise control plane  *(expansion)*

SSO · RBAC · separation of duties · policy management · evidence retention · a private
transparency service · SIEM · Jira/ServiceNow · on-premises · audit reports.

---

## Open-source versus commercial components

| Open source (trust) | Commercial (monetization) |
|---|---|
| receipt schema · verifier · canonicalization · signing interfaces · core domain · policy SDK · Git adapter · conformance suite | control plane · SSO/RBAC · policy management · evidence retention · integrations · private transparency log · reporting · multi-org · on-premises · compliance packs · incident forensics |

> A trust product should not demand blind trust in a closed format.
