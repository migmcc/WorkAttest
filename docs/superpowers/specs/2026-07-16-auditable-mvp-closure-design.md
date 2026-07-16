# Auditable MVP Closure Design

## Objective

Close the WorkAttest MVP lifecycle with evidence that can be independently checked. The
closure must reconcile ProjectPilot metadata, the project backlog, test evidence, and Git
state before recording the already-authorized human `done` approval.

## Scope

The closure will:

- create a dedicated `docs/TEST-REPORT.md` artifact from freshly executed checks;
- update `TASKS.md` only where repository evidence proves completion or partial completion;
- refresh stale ProjectPilot artifact records and register the test report;
- initialize a local Git repository and commit the project baseline;
- verify tests, the redaction CLI path, artifact hashes, Git cleanliness, and the
  ProjectPilot phase gate;
- execute `pp approve done` only after every objective gate is green;
- confirm the final ProjectPilot dashboard state.

The closure will not configure a remote, push, create a tag or release, repair the global
`pp.cmd` launcher, claim completion of market validation, or implement post-MVP features.

## Approach

Use a strict, fail-closed sequence. Documentation and metadata are updated first, followed
by fresh verification. Git records the reviewed baseline. The lifecycle approval is the
last state-changing command and is skipped if any preceding check fails.

This is preferable to a minimal gate-only close because it removes known inconsistencies
instead of merely satisfying ProjectPilot's filename matcher. It is also preferable to a
release-oriented close because no remote, release target, or versioning decision has been
authorized.

## Components and Responsibilities

### Test report

`docs/TEST-REPORT.md` is the machine-recognizable final-validation artifact. It records the
environment, exact commands, exit codes, observed test count, CLI redaction assertions,
scope, and known exclusions. It complements `docs/BUILD-EVIDENCE.md`; it does not replace
or rewrite historical evidence.

### Backlog reconciliation

`TASKS.md` is updated under an evidence-only rule:

- mark a task complete only if its full acceptance wording is demonstrated by current
  files and executed checks;
- leave partial tasks open and annotate the completed and missing portions;
- leave human work, especially market interviews, open;
- replace the obsolete execution-gate warning with the current final-validation state.

### Artifact inventory

ProjectPilot remains the only writer of `.project-pilot/artifacts.json`. The closure refreshes
the two known stale records, registers `docs/TEST-REPORT.md`, and re-registers any closure
documents changed after their previous registration. Verification independently compares
each selected record's path, size, and SHA-256 to the live file and rejects duplicate paths.

### Git baseline

The local repository tracks project source, tests, schemas, documentation, and ProjectPilot
state. Existing `.gitignore` rules exclude virtual environments, caches, build outputs,
private keys, receipts, editor state, and local WorkAttest key material. Before committing,
the staged file list is reviewed for secrets and generated files. The closure creates a
single baseline commit and requires a clean working tree before lifecycle approval.

### Lifecycle approval

The moved ProjectPilot installation at
`D:\Trabalho\_Concluidos\project-pilot` is invoked directly because the global `pp.cmd`
still points to its former location. `phase check --json` must report no missing
requirements and `ready_to_progress: true`. Only then is the user-authorized
`approve done` command executed with a reason summarizing verified tests, CLI evidence,
artifact integrity, and Git cleanliness.

## Validation Flow

1. Inspect repository files, ignored paths, and staged scope.
2. Run the full pytest suite through `.venv/Scripts/python.exe` and require exit code 0.
3. Run an isolated CLI smoke flow that creates, opens, redacts, verifies, and re-opens a
   receipt; require the final open to return the documented redacted result.
4. Remove only the smoke files created by the validation flow.
5. Register the test report and refreshed artifacts through ProjectPilot.
6. Compare registered sizes and SHA-256 values against all closure artifacts.
7. Require zero duplicate artifact paths.
8. Commit the reviewed baseline and require `git status --short` to be empty.
9. Require ProjectPilot's final-validation phase check to be ready.
10. Record the `done` approval and confirm the dashboard reports phase `done`.

## Failure Handling

Any failed command stops the sequence before approval. A test failure is reported as a code
or environment failure and is not copied into a passing report. A registry mismatch is
repaired through `pp artifact add`, never by hand-editing JSON. A suspected secret or
generated file is removed from the staged set and added to `.gitignore` when appropriate.
If ProjectPilot still rejects the test report, its phase matcher is inspected and the report
is renamed or structured to satisfy the documented requirement without weakening evidence.

## Success Criteria

The closure is complete only when all of the following are simultaneously true:

- the full test suite passes with zero failures;
- the redaction CLI smoke assertions pass;
- `docs/TEST-REPORT.md` exists and is registered;
- every closure artifact has matching size and SHA-256 metadata;
- ProjectPilot reports no missing final-validation requirements;
- Git has a baseline commit and a clean working tree;
- ProjectPilot records the authorized `done` approval and reports phase `done`;
- market validation and post-MVP features remain explicitly unclaimed.
