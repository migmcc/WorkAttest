"""A self-contained end-to-end scenario.

Builds a complete, signed WorkReceipt for an AI-assisted software change: a request,
an authorization scoped to ``src/``, an observed execution with a hash-chained action
log, verification results (including a mandatory passing test check), a bound human
approval, a deterministic policy decision, and Ed25519 signatures.

Used by the CLI ``demo`` command and by the test suite so both exercise the same path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .crypto.keys import KeyPair
from .domain.entities import (
    ArtifactEvidence,
    Authorization,
    ExecutionSession,
    PolicyRef,
    Subject,
    VerificationResult,
    WorkRequest,
)
from .domain.enums import Decision, RiskClass, SubjectType, VerificationStatus
from .approval import build_signed_approval
from .events import EventLog
from .hashing import HashRef, hash_canonical
from .policy import Policy, evaluate
from .receipts.issuer import ReceiptBuilder, result_hash_of

FIXED_TIME = "2026-01-01T12:00:00Z"


@dataclass
class ScenarioResult:
    receipt: dict[str, Any]
    issuer_key: KeyPair
    approver_key: KeyPair
    decision: Decision
    reasons: tuple[str, ...]


def build_accepted_receipt(
    now: str = FIXED_TIME,
    *,
    receipt_id: str = "rcpt-demo-001",
    previous_receipt_hash: str | None = None,
) -> ScenarioResult:
    issuer_key = KeyPair.generate()
    agent_key = KeyPair.generate()
    approver_key = KeyPair.generate()

    request = WorkRequest(
        id="req-001",
        title="Fix null-pointer in auth handler",
        intent="Correct a specific bug in the login handler",
        scope="src/ only",
        owner_subject="subj-human",
        risk_class=RiskClass.HIGH,  # high risk → requires human approval (INV-16)
        created_at=now,
        acceptance_criteria=("tests pass", "change confined to src/"),
    )

    subjects = [
        Subject(id="subj-human", type=SubjectType.HUMAN, public_key=approver_key.public_key_b64, issuer="local"),
        Subject(id="subj-agent", type=SubjectType.AGENT, public_key=agent_key.public_key_b64, issuer="local"),
    ]

    policy = Policy(id="pol-swchange", version="1.0.0", mandatory_check_ids=("tests", "lint"))

    authorization = Authorization(
        id="auth-001",
        request_id="req-001",
        subject_id="subj-agent",
        policy_id="pol-swchange",
        allowed_actions=("edit_file", "run_check"),
        allowed_resources=("src/auth/login.py",),
        issued_at=now,
        requires_approval=True,
        expires_at="2026-12-31T00:00:00Z",
    )

    execution = ExecutionSession(
        id="exec-001",
        request_id="req-001",
        authorization_id="auth-001",
        agent_subject_id="subj-agent",
        human_owner_id="subj-human",
        model="claude-opus-4-8",
        workspace="/repo",
        started_at=now,
        ended_at=now,
        status="completed",
    )

    log = EventLog()
    log.append("edit_file", "src/auth/login.py", observed_by="git", occurred_at=now,
               result_hash=hash_canonical({"diff": "+ null check"}))
    log.append("run_check", "tests", observed_by="verifier", occurred_at=now)
    actions_root = log.actions_root

    artifacts = [
        ArtifactEvidence(
            id="art-001",
            path_or_uri="src/auth/login.py",
            source="git",
            media_type="text/x-python",
            before_hash=hash_canonical({"v": "before"}),
            after_hash=hash_canonical({"v": "after"}),
            size=1024,
            classification="internal",
        )
    ]

    verification = [
        VerificationResult(
            id="vr-001", check_id="tests", check_version="1.0",
            definition_hash=hash_canonical({"check": "pytest -q"}),
            status=VerificationStatus.PASSED, tool="pytest", mandatory=True,
            exit_code=0, started_at=now, ended_at=now,
        ),
        VerificationResult(
            id="vr-002", check_id="lint", check_version="1.0",
            definition_hash=hash_canonical({"check": "ruff"}),
            status=VerificationStatus.PASSED, tool="ruff", mandatory=True,
            exit_code=0, started_at=now, ended_at=now,
        ),
    ]

    result_hash = result_hash_of(
        execution=execution, artifacts=artifacts, verification=verification, actions_root=actions_root
    )

    approval = build_signed_approval(
        execution_id="exec-001",
        approver_subject_id="subj-human",
        result_hash=result_hash,
        policy_id="pol-swchange",
        now=now,
        approver_key=approver_key,
        role="engineering-manager",
        justification="Reviewed the diff and passing checks; accepted.",
        approval_id="apr-001",
    )

    evaluation = evaluate(
        request=request,
        authorization=authorization,
        policy=policy,
        execution_id="exec-001",
        result_hash=result_hash,
        verification_results=verification,
        approvals=[approval],
        observed_actions=("edit_file", "run_check"),
        observed_resources=("src/auth/login.py",),
        now=now,
    )

    builder = ReceiptBuilder(
        request=request,
        subjects=subjects,
        authorization=authorization,
        execution=execution,
        actions_root=actions_root,
        policy=PolicyRef(policy_id=policy.id, version=policy.version, definition_hash=policy.definition_hash()),
        decision=evaluation.decision,
        artifacts=artifacts,
        verification=verification,
        approvals=[approval],
        issued_at=now,
        receipt_id=receipt_id,
        previous_receipt_hash=previous_receipt_hash,
        redactable={"reviewer_note": "Sensitive: root cause was a hardcoded token in login.py"},
    )
    receipt = builder.build_signed([issuer_key])

    return ScenarioResult(
        receipt=receipt,
        issuer_key=issuer_key,
        approver_key=approver_key,
        decision=evaluation.decision,
        reasons=evaluation.reasons,
    )
