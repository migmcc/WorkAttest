# TASKS — WorkAttest

Backlog for the A-team orchestrator (`/orchestrate morning` reads this). Tasks are
ordered; `depends_on` encodes sequencing. Status legend: `[ ]` pending · `[/]`
partial · `[x]` done.

> **Lifecycle note:** execution was approved on 2026-07-15 and the technical MVP reached
> final validation with a passing suite (103 tests today). Items remain open when their full wording is not
> proven, especially market interviews and property-based coverage.

---

## Phase 0 — finish discovery & contracts

- [ ] **TASK-001** Review & ratify the receipt schema v1 (`schemas/work-receipt.schema.json`) with a threat lens. `depends_on: null` — route: security-reviewer + architect.
- [ ] **TASK-002** Cross-check INVARIANTS ↔ THREAT-MODEL ↔ receipt schema for full coverage (every INV has a test hook and a schema anchor). `depends_on: null` — route: architect.
- [x] **TASK-003** Draft `SECURITY.md` (coordinated disclosure, threat model pointer, key-handling policy). `depends_on: null` — route: security-reviewer.
- [ ] **TASK-004** Start market-validation interviews (idea §19) — **binding approval condition**; track willingness-to-pay. `depends_on: null` — route: human (not an agent task).
- [ ] **TASK-005** Phase 0 gate review: trust model reviewed, receipt v1 approved, first use case closed, zero absolute-guarantee claims. `depends_on: TASK-001, TASK-002` — route: architect + compliance-reviewer.

## Phase 1 — deterministic core

- [x] **TASK-101** Scaffold repo: `pyproject.toml`, `src/workattest/` package layout (domain/identity/policy/... per idea §16), `tests/` tree, README, LICENSE. `depends_on: TASK-005` — route: architect → python-reviewer.
- [/] **TASK-102** Canonical JSON serialization (RFC 8785 / JCS) with property-based round-trip tests (INV-12). Implementation and unit tests exist; RFC 8785 conformance and property-based coverage remain open. `depends_on: TASK-101` — route: tdd-guide → python-reviewer.
- [/] **TASK-103** Domain entities + state machine (WorkRequest, Subject, Authorization, ExecutionSession, ActionEvent, ArtifactEvidence, VerificationResult, ApprovalDecision, WorkReceipt). Entities and enums exist; a formally tested lifecycle state machine remains open. `depends_on: TASK-101` — route: architect → python-reviewer.
- [/] **TASK-104** Append-only event log with hash chain (`previous_event_hash`, `actions_root`) + property tests (INV-11). Implementation and unit tests exist; property-based coverage remains open. `depends_on: TASK-103` — route: tdd-guide → security-reviewer.
- [x] **TASK-105** Deterministic policy engine → `ACCEPT/HOLD/REFUSE`, versioned + hashable (INV-7, INV-8, INV-18, INV-20). `depends_on: TASK-103` — route: security-reviewer.
- [x] **TASK-106** Storage interfaces (ports) + local filesystem adapter. `depends_on: TASK-103` — route: python-reviewer.
- [/] **TASK-107** Minimal CLI skeleton wiring the above commands. The operational CLI provides `init`, `keygen`, `demo`, `observe-git`, and receipt operations; the originally named `request create` and `policy evaluate` commands remain open. `depends_on: TASK-105, TASK-106` — route: python-reviewer.
- [ ] **TASK-108** Phase 1 gate review: domain infra-independent, policy deterministic + tested, invariants covered. `depends_on: TASK-102, TASK-104, TASK-105, TASK-107` — route: code-reviewer + security-reviewer.

## Backlog (Phase 2+ — crypto receipts, Git adapter, verifier)

- [x] **TASK-201** Ed25519 signing + verification + key model (INV-13/15).
- [x] **TASK-202** Receipt issuer (canonical + signed) and offline verifier (`receipt verify`).
- [x] **TASK-203** Adversarial tamper suite T-1…T-12 (see THREAT-MODEL §4). All twelve are covered; THREAT-MODEL §4 maps each one to its test.
- [x] **TASK-301** Git adapter (snapshots, diffs, artifact hashes) + command observation.
- [x] **TASK-302** Verifier runner for operator-defined checks (INV-5).
- [/] **TASK-303** End-to-end demo: Claude/Codex → Git → signed receipt → offline verify on another machine. Cross-machine verification is proven: static vectors signed on the maintainer's machine are verified in CI on Linux, macOS and Windows (T-11, `tests/vectors/`). Driving the chain from a real Claude/Codex session is still done by hand.

## Additional verified increments

- [x] Receipt chains with ordered-link verification and adversarial reorder detection.
- [x] Salted field commitments with redact/open CLI operations and disclosure-tamper detection.
