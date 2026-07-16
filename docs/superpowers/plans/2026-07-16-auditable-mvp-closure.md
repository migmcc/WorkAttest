# Auditable MVP Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the WorkAttest MVP with fresh test evidence, reconciled documentation and artifact metadata, a reviewed Git baseline, and the user-authorized ProjectPilot `done` approval.

**Architecture:** Execute a fail-closed pipeline: gather evidence, write the test report and backlog reconciliation, register and verify artifact metadata, commit the complete local baseline, then record the lifecycle approval. ProjectPilot remains the only writer of its artifact inventory, and approval is skipped if any objective gate fails.

**Tech Stack:** Python 3.13.14, pytest 9.1.1, PowerShell 7, Git, ProjectPilot 1.0.0.

## Global Constraints

- Do not configure a Git remote, push, create a tag, or create a release.
- Do not repair or modify `D:\Trabalho\bin\pp.cmd` during this closure.
- Invoke ProjectPilot through `D:\Trabalho\_Concluidos\project-pilot\.venv\Scripts\python.exe -m projectpilot`.
- Never edit `.project-pilot/artifacts.json` by hand; use `projectpilot artifact add`.
- Stop before `approve done` if tests, CLI smoke assertions, registry integrity, Git cleanliness, or `phase check` fail.
- Keep market validation, full T-1…T-12 coverage, cross-machine verification, OIDC/SSO, and the transparency log explicitly unclaimed.
- Never stage `.venv/`, cache directories, private keys, `.workattest/`, or generated receipts.

---

### Task 1: Gather fresh verification evidence

**Files:**
- Temporary: `.closure-smoke-receipt.json`
- Temporary: `.closure-smoke-redacted.json`
- Verify: `tests/`

**Interfaces:**
- Consumes: the installed `workattest` package and current test suite.
- Produces: observed full-suite and CLI results used verbatim by `docs/TEST-REPORT.md`.

- [ ] **Step 1: Run the full suite**

Run:

```powershell
& '.venv\Scripts\python.exe' -m pytest
exit $LASTEXITCODE
```

Expected: exit 0 and `85 passed` with zero failures.

- [ ] **Step 2: Run the complete redaction CLI smoke flow**

Run:

```powershell
$receipt = Join-Path (Get-Location) '.closure-smoke-receipt.json'
$redacted = Join-Path (Get-Location) '.closure-smoke-redacted.json'
& '.venv\Scripts\python.exe' -m workattest.cli demo --out $receipt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& '.venv\Scripts\python.exe' -m workattest.cli receipt open $receipt reviewer_note
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& '.venv\Scripts\python.exe' -m workattest.cli receipt redact $receipt --field reviewer_note --out $redacted
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& '.venv\Scripts\python.exe' -m workattest.cli receipt verify $redacted
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& '.venv\Scripts\python.exe' -m workattest.cli receipt open $redacted reviewer_note 2>&1
$redactedOpenExit = $LASTEXITCODE
$originalJson = Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
$redactedJson = Get-Content -LiteralPath $redacted -Raw | ConvertFrom-Json
$hashUnchanged = $originalJson.receipt_hash -eq $redactedJson.receipt_hash
$signaturesUnchanged = ($originalJson.signatures | ConvertTo-Json -Compress -Depth 100) -eq ($redactedJson.signatures | ConvertTo-Json -Compress -Depth 100)
$disclosureRemoved = $null -eq $redactedJson.disclosures
if ($redactedOpenExit -ne 1 -or -not $hashUnchanged -or -not $signaturesUnchanged -or -not $disclosureRemoved) { exit 1 }
Write-Output 'CLI_SMOKE_OK open_before=0 redact=0 verify=0 open_after=1 hash_unchanged=true signatures_unchanged=true disclosure_removed=true'
exit 0
```

Expected: exit 0, both receipt verifications report `Receipt VALID`, and the final line is `CLI_SMOKE_OK ...`.

- [ ] **Step 3: Remove only the two smoke files after validating their resolved paths**

Run:

```powershell
$workspace = (Resolve-Path -LiteralPath '.').Path.TrimEnd('\')
foreach ($target in @('.closure-smoke-receipt.json', '.closure-smoke-redacted.json')) {
  if (Test-Path -LiteralPath $target) {
    $resolved = (Resolve-Path -LiteralPath $target).Path
    if (-not $resolved.StartsWith($workspace + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
      throw "Refusing to remove path outside workspace: $resolved"
    }
    Remove-Item -LiteralPath $resolved -Force
  }
}
if ((Test-Path -LiteralPath '.closure-smoke-receipt.json') -or
    (Test-Path -LiteralPath '.closure-smoke-redacted.json')) {
  throw 'Smoke files still exist after cleanup'
}
Write-Output 'SMOKE_CLEANUP_OK'
```

Expected: both temporary files are absent and no project file is removed.

---

### Task 2: Create the test report and reconcile the backlog

**Files:**
- Create: `docs/TEST-REPORT.md`
- Modify: `TASKS.md`

**Interfaces:**
- Consumes: Task 1's observed `85 passed` and CLI assertion results.
- Produces: the `test-report` artifact required by ProjectPilot and a truthful backlog snapshot.

- [ ] **Step 1: Create the final-validation test report**

Create `docs/TEST-REPORT.md` with exactly this evidence structure:

````markdown
# TEST REPORT — WorkAttest MVP

Date: 2026-07-16  
Lifecycle phase at execution: `final-validation`

## Environment

- Python 3.13.14
- pytest 9.1.1
- cryptography 49.0.0
- package installed editable from this workspace

## Full automated suite

Command:

```text
.venv/Scripts/python -m pytest
```

Observed result: `85 passed`; exit code `0`; zero failures.

Coverage includes canonical serialization, hashing, Ed25519 signing and verification,
hash-chained events, deterministic policy decisions, signed approvals, receipt issue and
offline verification, receipt chains, Git adapter integration, operator-defined checks,
adversarial tampering, salted commitments, redaction, and disclosure integrity.

## Redaction CLI smoke test

The public CLI was exercised end to end:

1. create a signed demo receipt;
2. open `reviewer_note` before redaction — exit `0`;
3. redact `reviewer_note` — redacted receipt `VALID`, exit `0`;
4. verify the redacted receipt independently — `VALID`, exit `0`;
5. open `reviewer_note` after redaction — documented redacted result, exit `1`.

Explicit assertions passed: the disclosure was removed while `receipt_hash` and signatures
remained unchanged.

## Result

The implemented WorkAttest MVP core is verified for the tested local environment.

## Explicit exclusions

This report does not claim completed market interviews, full T-1…T-12 adversarial coverage,
verification on a second machine, OIDC/SSO identity, a transparency log, or general proof of
the correctness of AI-produced work.
````

- [ ] **Step 2: Reconcile `TASKS.md` under the evidence-only rule**

Replace the file with this complete reconciled content:

````markdown
# TASKS — WorkAttest

Backlog for the A-team orchestrator (`/orchestrate morning` reads this). Tasks are
ordered; `depends_on` encodes sequencing. Status legend: `[ ]` pending · `[/]`
partial · `[x]` done.

> **Lifecycle note:** execution was approved on 2026-07-15 and the technical MVP reached
> final validation with 85 passing tests. Items remain open when their full wording is not
> proven, especially market interviews, property-based coverage, the complete T-1…T-12
> suite, and cross-machine verification.

---

## Fase 0 — finish discovery & contracts

- [ ] **TASK-001** Review & ratify the receipt schema v1 (`schemas/work-receipt.schema.json`) with a threat lens. `depends_on: null` — route: security-reviewer + architect.
- [ ] **TASK-002** Cross-check INVARIANTS ↔ THREAT-MODEL ↔ receipt schema for full coverage (every INV has a test hook and a schema anchor). `depends_on: null` — route: architect.
- [x] **TASK-003** Draft `SECURITY.md` (coordinated disclosure, threat model pointer, key-handling policy). `depends_on: null` — route: security-reviewer.
- [ ] **TASK-004** Start market-validation interviews (idea §19) — **binding approval condition**; track willingness-to-pay. `depends_on: null` — route: human (not an agent task).
- [ ] **TASK-005** Fase 0 gate review: trust model reviewed, receipt v1 approved, first use case closed, zero absolute-guarantee claims. `depends_on: TASK-001, TASK-002` — route: architect + compliance-reviewer.

## Fase 1 — core determinístico

- [x] **TASK-101** Scaffold repo: `pyproject.toml`, `src/workattest/` package layout (domain/identity/policy/... per idea §16), `tests/` tree, README, LICENSE. `depends_on: TASK-005` — route: architect → python-reviewer.
- [/] **TASK-102** Canonical JSON serialization (RFC 8785 / JCS) with property-based round-trip tests (INV-12). Implementation and unit tests exist; RFC 8785 conformance and property-based coverage remain open. `depends_on: TASK-101` — route: tdd-guide → python-reviewer.
- [/] **TASK-103** Domain entities + state machine (WorkRequest, Subject, Authorization, ExecutionSession, ActionEvent, ArtifactEvidence, VerificationResult, ApprovalDecision, WorkReceipt). Entities and enums exist; a formally tested lifecycle state machine remains open. `depends_on: TASK-101` — route: architect → python-reviewer.
- [/] **TASK-104** Append-only event log with hash chain (`previous_event_hash`, `actions_root`) + property tests (INV-11). Implementation and unit tests exist; property-based coverage remains open. `depends_on: TASK-103` — route: tdd-guide → security-reviewer.
- [x] **TASK-105** Deterministic policy engine → `ACCEPT/HOLD/REFUSE`, versioned + hashable (INV-7, INV-8, INV-18, INV-20). `depends_on: TASK-103` — route: security-reviewer.
- [x] **TASK-106** Storage interfaces (ports) + local filesystem adapter. `depends_on: TASK-103` — route: python-reviewer.
- [/] **TASK-107** Minimal CLI skeleton wiring the above commands. The operational CLI provides `init`, `keygen`, `demo`, `observe-git`, and receipt operations; the originally named `request create` and `policy evaluate` commands remain open. `depends_on: TASK-105, TASK-106` — route: python-reviewer.
- [ ] **TASK-108** Fase 1 gate review: domain infra-independent, policy deterministic + tested, invariants covered. `depends_on: TASK-102, TASK-104, TASK-105, TASK-107` — route: code-reviewer + security-reviewer.

## Backlog (Fase 2+ — crypto receipts, Git adapter, verifier)

- [x] **TASK-201** Ed25519 signing + verification + key model (INV-13/15).
- [x] **TASK-202** Receipt issuer (canonical + signed) and offline verifier (`receipt verify`).
- [/] **TASK-203** Adversarial tamper suite T-1…T-12 (see THREAT-MODEL §4). Implemented cases are green; the complete T-1…T-12 mapping remains open.
- [x] **TASK-301** Git adapter (snapshots, diffs, artifact hashes) + command observation.
- [x] **TASK-302** Verifier runner for operator-defined checks (INV-5).
- [/] **TASK-303** End-to-end demo: Claude/Codex → Git → signed receipt → offline verify on another machine. The local signed demo is green; verification on another machine remains open.

## Additional verified increments

- [x] Receipt chains with ordered-link verification and adversarial reorder detection.
- [x] Salted field commitments with redact/open CLI operations and disclosure-tamper detection.
````

- [ ] **Step 3: Verify that the report and backlog do not overclaim excluded work**

Run:

```powershell
rg -n "85 passed|CLI|Explicit exclusions|market|T-1…T-12|second machine|OIDC|transparency" docs/TEST-REPORT.md TASKS.md
```

Expected: evidence and exclusions appear in both documents; market validation remains `[ ]`.

- [ ] **Step 4: Commit the evidence documents**

Run:

```powershell
git add -- docs/TEST-REPORT.md TASKS.md
git commit -m "docs: record MVP validation evidence"
```

Expected: commit succeeds and includes exactly the two files.

---

### Task 3: Register and verify closure artifacts

**Files:**
- Modify through ProjectPilot only: `.project-pilot/artifacts.json`
- Register: `docs/TEST-REPORT.md`
- Register: `TASKS.md`
- Refresh: `src/workattest/adapters/git/flow.py`
- Refresh: `tests/integration/test_git_adapter.py`
- Register: `docs/superpowers/specs/2026-07-16-auditable-mvp-closure-design.md`
- Register: `docs/superpowers/plans/2026-07-16-auditable-mvp-closure.md`

**Interfaces:**
- Consumes: verified files from Tasks 1–2 and the committed closure spec/plan.
- Produces: current ProjectPilot SHA-256/size metadata and a satisfied final-validation requirement.

- [ ] **Step 1: Register or refresh all closure artifacts**

Run:

```powershell
$ppPython = 'D:\Trabalho\_Concluidos\project-pilot\.venv\Scripts\python.exe'
$files = @(
  'docs/TEST-REPORT.md',
  'TASKS.md',
  'src/workattest/adapters/git/flow.py',
  'tests/integration/test_git_adapter.py',
  'docs/superpowers/specs/2026-07-16-auditable-mvp-closure-design.md',
  'docs/superpowers/plans/2026-07-16-auditable-mvp-closure.md'
)
foreach ($file in $files) {
  & $ppPython -m projectpilot artifact add $file
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
```

Expected: six `Registered artifact:` lines and exit 0.

- [ ] **Step 2: Verify the complete inventory, not only the six refreshed records**

Run:

```powershell
$inventory = Get-Content -LiteralPath '.project-pilot\artifacts.json' -Raw | ConvertFrom-Json
$duplicates = @($inventory.artifacts | Group-Object path | Where-Object Count -ne 1)
if ($duplicates.Count -ne 0) { throw "Duplicate artifact paths: $($duplicates.Name -join ', ')" }
foreach ($record in $inventory.artifacts) {
  if (-not (Test-Path -LiteralPath $record.path -PathType Leaf)) { throw "Missing artifact: $($record.path)" }
  $item = Get-Item -LiteralPath $record.path
  $hash = (Get-FileHash -LiteralPath $record.path -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($record.sha256 -ne $hash) { throw "SHA-256 mismatch: $($record.path)" }
  if ([int64]$record.size -ne $item.Length) { throw "Size mismatch: $($record.path)" }
}
Write-Output "ARTIFACTS_OK total=$($inventory.artifacts.Count) duplicate_paths=0"
```

Expected: one `ARTIFACTS_OK` line and no exception.

- [ ] **Step 3: Verify the ProjectPilot phase requirement**

Run:

```powershell
$ppPython = 'D:\Trabalho\_Concluidos\project-pilot\.venv\Scripts\python.exe'
& $ppPython -m projectpilot phase check --json
exit $LASTEXITCODE
```

Expected JSON: `completion: 100`, `ready_to_progress: true`, `completed: ["test-report"]`, and `missing: []`.

- [ ] **Step 4: Commit the artifact inventory**

Run:

```powershell
git add -- .project-pilot/artifacts.json
git commit -m "chore: register MVP closure evidence"
```

Expected: commit succeeds and contains only the inventory update.

---

### Task 4: Commit the reviewed project baseline

**Files:**
- Add: all remaining project source, tests, schemas, documentation, and ProjectPilot state.
- Exclude: every path matched by `.gitignore`.

**Interfaces:**
- Consumes: the current workspace after Tasks 1–3.
- Produces: a complete local Git baseline with no secret or generated file staged.

- [ ] **Step 1: Review all untracked and ignored paths**

Run:

```powershell
git status --short
git status --short --ignored
```

Expected: `.venv/`, `.pytest_cache/`, `*.egg-info/`, and Python caches appear only as ignored; project source/docs appear untracked.

- [ ] **Step 2: Stage the explicit project baseline**

Run:

```powershell
git add -- .agent-sync .gitignore .project-pilot/status.json CONTRIBUTING.md INIT.md LICENSE PROJECT_BRIEF.md README.md SECURITY.md docs ideia-workattest.md pyproject.toml schemas src tests
```

Expected: all intended project material is staged, with no ignored local/runtime material.

- [ ] **Step 3: Audit the staged file list and secret markers**

Run:

```powershell
$staged = @(git diff --cached --name-only)
$forbidden = @($staged | Where-Object { $_ -match '(^|/)(\.venv|\.pytest_cache|__pycache__|\.workattest)(/|$)|\.pem$|receipt\.json$|\.egg-info/' })
if ($forbidden.Count -ne 0) { throw "Forbidden staged paths: $($forbidden -join ', ')" }
$secretFiles = @(git grep --cached -Il -E -- '-----BEGIN [A-Z ]*PRIVATE KEY-----|sk-[A-Za-z0-9_-]{20,}')
if ($secretFiles.Count -ne 0) { throw "Possible secrets in staged files: $($secretFiles -join ', ')" }
Write-Output "STAGING_OK files=$($staged.Count) forbidden=0 secret_markers=0"
```

Expected: `STAGING_OK` and no listed forbidden/secret file.

- [ ] **Step 4: Commit the baseline**

Run:

```powershell
git commit -m "chore: establish verified WorkAttest MVP baseline"
```

Expected: commit succeeds.

- [ ] **Step 5: Require a clean tree before lifecycle approval**

Run:

```powershell
$dirty = @(git status --short)
if ($dirty.Count -ne 0) { throw "Working tree is not clean: $($dirty -join '; ')" }
Write-Output 'GIT_CLEAN before_done=true'
```

Expected: `GIT_CLEAN before_done=true`.

---

### Task 5: Record the authorized lifecycle completion

**Files:**
- Modify through ProjectPilot: `.project-pilot/status.json`

**Interfaces:**
- Consumes: green phase readiness, clean Git state, and the user's explicit approval.
- Produces: ProjectPilot phase `done` and a committed approval record.

- [ ] **Step 1: Recheck the gate immediately before approval**

Run:

```powershell
$ppPython = 'D:\Trabalho\_Concluidos\project-pilot\.venv\Scripts\python.exe'
& $ppPython -m projectpilot phase check --json
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if (@(git status --short).Count -ne 0) { throw 'Working tree became dirty before approval' }
```

Expected: final-validation is 100% ready and Git is clean.

- [ ] **Step 2: Execute the user-authorized `done` approval**

Run:

```powershell
$ppPython = 'D:\Trabalho\_Concluidos\project-pilot\.venv\Scripts\python.exe'
& $ppPython -m projectpilot approve done --reason 'MVP core verified: 85 tests passing, redaction CLI smoke green, artifact hashes current, and Git baseline clean.'
exit $LASTEXITCODE
```

Expected: exit 0 and ProjectPilot advances to `done`.

- [ ] **Step 3: Verify the dashboard state before committing it**

Run:

```powershell
$ppPython = 'D:\Trabalho\_Concluidos\project-pilot\.venv\Scripts\python.exe'
& $ppPython -m projectpilot dashboard --json
exit $LASTEXITCODE
```

Expected JSON: project phase `done` and no failed command.

- [ ] **Step 4: Commit the lifecycle approval record**

Run:

```powershell
git add -- .project-pilot/status.json
git commit -m "chore: record ProjectPilot completion"
```

Expected: commit succeeds and contains only `.project-pilot/status.json`.

---

### Task 6: Run final independent verification

**Files:**
- Verify: `.project-pilot/artifacts.json`
- Verify: `.project-pilot/status.json`
- Verify: Git repository and full Python test suite.

**Interfaces:**
- Consumes: the completed lifecycle and committed baseline.
- Produces: final evidence supporting the completion claim.

- [ ] **Step 1: Rerun the full test suite after all closure changes**

Run:

```powershell
& '.venv\Scripts\python.exe' -m pytest
exit $LASTEXITCODE
```

Expected: exit 0 and `85 passed`.

- [ ] **Step 2: Recheck every artifact hash and duplicate path**

Run:

```powershell
$inventory = Get-Content -LiteralPath '.project-pilot\artifacts.json' -Raw | ConvertFrom-Json
$duplicates = @($inventory.artifacts | Group-Object path | Where-Object Count -ne 1)
if ($duplicates.Count -ne 0) { throw "Duplicate artifact paths: $($duplicates.Name -join ', ')" }
foreach ($record in $inventory.artifacts) {
  if (-not (Test-Path -LiteralPath $record.path -PathType Leaf)) { throw "Missing artifact: $($record.path)" }
  $item = Get-Item -LiteralPath $record.path
  $hash = (Get-FileHash -LiteralPath $record.path -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($record.sha256 -ne $hash) { throw "SHA-256 mismatch: $($record.path)" }
  if ([int64]$record.size -ne $item.Length) { throw "Size mismatch: $($record.path)" }
}
Write-Output "ARTIFACTS_OK total=$($inventory.artifacts.Count) duplicate_paths=0"
```

Expected: `ARTIFACTS_OK` with zero mismatches and zero duplicate paths.

- [ ] **Step 3: Verify final lifecycle and Git state**

Run:

```powershell
$ppPython = 'D:\Trabalho\_Concluidos\project-pilot\.venv\Scripts\python.exe'
$dashboardLines = & $ppPython -m projectpilot dashboard --json
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$dashboard = ($dashboardLines -join [Environment]::NewLine) | ConvertFrom-Json
if ($dashboard.project.phase -ne 'done') { throw "Unexpected phase: $($dashboard.project.phase)" }
$dirty = @(git status --short)
if ($dirty.Count -ne 0) { throw "Working tree is not clean: $($dirty -join '; ')" }
git log --oneline --decorate -5
Write-Output 'CLOSURE_OK phase=done git_clean=true tests=85 artifacts=verified'
```

Expected: `CLOSURE_OK phase=done git_clean=true tests=85 artifacts=verified`.
