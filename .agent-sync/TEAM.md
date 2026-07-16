# Active Team — WorkAttest

Generated: 2026-07-15 (authored manually, non-destructively)

> **Note:** This team was selected by evaluating `INIT.md` against the orchestrator's
> keep/prune rules. It was authored by hand rather than by `/orchestrate init` because
> WorkAttest has no local `.claude/agents/` or `skills/` directory — running the
> orchestrator's INIT prune (`rm .claude/agents/*`, `rm -rf skills/*`) would have
> operated on the shared `00_Base` config. **No files were deleted.** "Pruned" below
> means "not part of this project's active team", not removed from disk.

## Active Agents

- **python-reviewer** — Python is the only language.
- **security-reviewer** — crypto/signing/identity/threat-model are core; security-critical project.
- **code-reviewer** — all code changes.
- **architect** — system design + ADRs for domain, policy engine, receipt format.
- **planner** — complex feature planning across phases.
- **compliance-reviewer** — complianceScope = GDPR/RGPD (data minimization, redaction, evidence classification).
- **doc-updater** — contracts-first project with heavy documentation.
- **debugger** — active development; systematic root-cause debugging.
- **build-error-resolver** — Python build/type error triage.
- **refactor-cleaner** — dead-code/duplication cleanup during active dev.
- **tdd-guide** — invariants and adversarial tests demand test-first discipline.
- **harness-optimizer** — always kept (pipeline audit).

## Pruned Agents (not in this project's active team; NOT deleted)

- **go-reviewer / rust-reviewer / kotlin-reviewer / swift-reviewer / flutter-reviewer** — no Go/Rust/Kotlin/Swift/Dart.
- **database-reviewer** — no relational/PostgreSQL database in the MVP.
- **infra-reviewer** — no Terraform/Docker/K8s/CI IaC in the MVP (reconsider at GitHub App / enterprise phases).
- **ai-reviewer** — core makes no LLM API calls (reconsider when building agent-observation/MCP adapters).
- **e2e-runner** — no web UI; the demo is a CLI scenario, not browser E2E.
- **performance-profiler** — no performance targets declared for the MVP.
- **chief-of-staff** — no email/Slack/communication tooling.
- **loop-operator** — no autonomous loops.

## Active Skills

- **brainstorming** — greenfield.
- **writing-plans / executing-plans / subagent-driven-development** — active development with independent tasks.
- **systematic-debugging** — active development.
- **test-driven-development** — RED before GREEN for invariants and adversarial tests.
- **verification-before-completion** — evidence before completion claims.
- **requesting-code-review / receiving-code-review** — review discipline.
- **using-git-worktrees** — isolation for feature work.
- **finishing-a-development-branch** — feature-branch workflow.
- **api-contract-first** — schema-first design (the receipt JSON Schema is the contract).
- **dispatching-parallel-agents** — parallel independent tasks expected.
- **writing-skills** — for maintaining the toolkit.

## Pruned Skills (not active; NOT deleted)

- **data-migration** — no database in the MVP.
- **incident-response** — no production environment yet.
- **performance-audit** — no performance targets declared for the MVP.

## Reconsider triggers

- Add **infra-reviewer** when the GitHub App / CI packaging work starts (Fase 6).
- Add **ai-reviewer** when agent-observation / MCP adapters are built.
- Add **database-reviewer** + **data-migration** if the enterprise control plane introduces a database (Fase 7).
