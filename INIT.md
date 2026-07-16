# INIT — WorkAttest

Project initialization contract for the A-team orchestrator. Read by `/orchestrate init`
to select the active team and routing. See `.agent-sync/TEAM.md` and `.agent-sync/ROUTING.md`.

## Project

- **name:** WorkAttest
- **slug:** workattest
- **type:** greenfield / active-development
- **stage:** planning (MVP — Fase 0/1 of the roadmap)
- **one-liner:** Local-first, verifiable infrastructure that cryptographically links
  request → identity → authorization → execution → evidence → verification → human
  approval to a signed receipt for AI-assisted work.
- **category:** Verifiable Work Accountability
- **first wedge:** AI software change accountability (demonstrable on a PR)

## Languages

- Python (primary — core domain, policy engine, CLI, verifier)

> No Go, Rust, Kotlin, Swift, Dart, Java/Android, or frontend languages in the MVP.

## Tech stack

- CLI + library (`workattest ...`)
- Cryptography: Ed25519 signatures, canonical JSON (RFC 8785 / JCS)
- Adapters: Git (snapshots/diffs/hashes), filesystem (evidence)
- Storage: interfaces + local files (append-only event log with hash chain)
- **No** relational/PostgreSQL database in the MVP
- **No** Docker / Kubernetes / Terraform in the MVP (packaging via pyproject)
- Standards to align with: in-toto, DSSE, Sigstore (evaluate), SLSA, OIDC (CI)

## Interfaces / contracts

- **hasApiEndpoints:** no REST/gRPC/GraphQL in the MVP; the CLI and the
  `work-receipt` JSON Schema are the primary contracts (schema-first design applies)
- **contractFiles:** `schemas/work-receipt.schema.json`

## AI

- **makesLlmApiCalls:** no — the product *observes* AI agents but the core makes no LLM
  calls. (Becomes relevant later when building agent-observation/MCP adapters.)
- **aiNative:** domain is AI-accountability, but no model calls in core logic

## Quality & process

- **gitWorkflow:** feature-branches
- **testing:** unit + property-based + **adversarial** (tamper/cross-execution) + conformance
- **e2eTests:** no (no web UI; the "demo" is a CLI end-to-end scenario, not browser E2E)
- **documentation:** yes (heavy — contracts-first project)
- **performanceTargets:** none declared for MVP (correctness & security first)
- **autonomousLoops:** no
- **productionEnvironment:** not yet (pre-MVP)

## Compliance & constraints

- **complianceScope:** GDPR/RGPD (data minimization, redaction, evidence classification —
  INV-19). SOC2 relevant for the future enterprise control plane (out of MVP scope).
- **specialConstraints:**
  - Security- and cryptography-critical: signing, hashing, threat model are core.
    Any change to crypto/identity/policy/receipt requires security review.
  - Fail-safe: identity/policy/signature/verification failures must close to HOLD/REFUSE,
    never ACCEPT (INV-20).
  - The agent never selects the checks that verify it (INV-5).
  - No absolute-guarantee claims: the product promise is procedural/probatory, not
    correctness (see docs/ACCOUNTABILITY-MODEL.md §3).
  - Human approval gates stay explicit and auditable (see global charter).

## Notes

- Reuse (as clients/donors, not core): ProjectPilot, Taevdar, Agent Trust Gate.
- Binding validation condition: run market-validation interviews (idea §19) in parallel;
  willingness-to-pay is the primary kill criterion (idea §21).
