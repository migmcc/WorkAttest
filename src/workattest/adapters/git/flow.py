"""Turn an observed Git change into a signed WorkReceipt.

This wires the Git adapter into the deterministic core: observe → evidence → policy →
receipt. It enforces directory scope — a change touching files outside the authorized
prefix yields HOLD/REFUSE (PRD §6 step 7) — and produces a receipt that verifies offline.

Kept deliberately opinionated for the MVP demo: low-risk by default (no human approval
required) so the focus is evidence capture and scope enforcement. Callers needing
mandatory checks or approvals compose the core APIs directly (see scenario.py).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Sequence

from ...crypto.keys import KeyPair
from ...domain.entities import (
    Authorization,
    ExecutionSession,
    PolicyRef,
    Subject,
    WorkRequest,
)
from ...domain.enums import Decision, RiskClass, SubjectType
from ...approval import build_signed_approval
from ...events import EventLog
from ...policy import Policy, evaluate
from ...receipts.issuer import ReceiptBuilder, result_hash_of
from ...verification import Check, run_checks
from .adapter import WORKTREE, GitAdapter


def _action_for(before_hash: object, after_hash: object) -> str:
    if before_hash is None:
        return "add_file"
    if after_hash is None:
        return "delete_file"
    return "edit_file"


@dataclass
class GitReceiptResult:
    receipt: dict[str, Any]
    decision: Decision
    reasons: tuple[str, ...]
    changed_paths: tuple[str, ...]
    before_commit: Optional[str]


def build_change_receipt(
    *,
    repo_path: str,
    before_ref: str,
    after_ref: Optional[str] = WORKTREE,
    allowed_prefix: str = "src/",
    issuer_key: KeyPair,
    agent_key: KeyPair,
    now: str,
    intent: str = "AI-assisted software change",
    risk: RiskClass = RiskClass.LOW,
    checks: Sequence[Check] = (),
    approver_key: Optional[KeyPair] = None,
    approval_justification: str = "Reviewed and accepted.",
) -> GitReceiptResult:
    adapter = GitAdapter(repo_path)
    before_commit = adapter.head_commit() if before_ref in ("HEAD", None) else before_ref

    artifacts = adapter.collect_artifacts(before_ref, after_ref)
    changed_paths = tuple(a.path_or_uri for a in artifacts)

    # Run operator-defined checks against the working tree (INV-5: the agent does not
    # choose these). Their real results feed both the receipt and the policy decision.
    verification = tuple(run_checks(checks, repo_path))
    mandatory_ids = tuple(c.id for c in checks if c.mandatory)

    log = EventLog()
    for art in artifacts:
        log.append(
            _action_for(art.before_hash, art.after_hash),
            art.path_or_uri,
            observed_by="git",
            occurred_at=now,
            result_hash=art.after_hash or art.before_hash,
        )
    actions_root = log.actions_root
    observed_actions = sorted({_action_for(a.before_hash, a.after_hash) for a in artifacts})

    request = WorkRequest(
        id="req-git",
        intent=intent,
        scope=f"changes under {allowed_prefix}",
        owner_subject="subj-human",
        risk_class=risk,
        created_at=now,
    )
    human_pub = (approver_key or issuer_key).public_key_b64
    subjects = [
        Subject(id="subj-human", type=SubjectType.HUMAN, public_key=human_pub, issuer="local"),
        Subject(id="subj-agent", type=SubjectType.AGENT, public_key=agent_key.public_key_b64, issuer="local"),
    ]
    policy = Policy(id="pol-git", version="1.0.0", mandatory_check_ids=mandatory_ids)
    authorization = Authorization(
        id="auth-git",
        request_id="req-git",
        subject_id="subj-agent",
        policy_id="pol-git",
        allowed_actions=("add_file", "edit_file", "delete_file", "run_check"),
        allowed_resources=(f"{allowed_prefix}**",),
        issued_at=now,
        requires_approval=risk.requires_human_approval,
    )
    execution = ExecutionSession(
        id="exec-git",
        request_id="req-git",
        authorization_id="auth-git",
        agent_subject_id="subj-agent",
        human_owner_id="subj-human",
        workspace=str(repo_path),
        started_at=now,
        ended_at=now,
        status="completed",
    )

    result_hash = result_hash_of(
        execution=execution, artifacts=artifacts, verification=verification, actions_root=actions_root
    )

    approvals = ()
    if approver_key is not None:
        approvals = (
            build_signed_approval(
                execution_id="exec-git",
                approver_subject_id="subj-human",
                result_hash=result_hash,
                policy_id=policy.id,
                now=now,
                approver_key=approver_key,
                justification=approval_justification,
            ),
        )

    evaluation = evaluate(
        request=request,
        authorization=authorization,
        policy=policy,
        execution_id="exec-git",
        result_hash=result_hash,
        verification_results=verification,
        approvals=approvals,
        observed_actions=observed_actions,
        observed_resources=changed_paths,
        now=now,
    )

    receipt = ReceiptBuilder(
        request=request,
        subjects=subjects,
        authorization=authorization,
        execution=execution,
        actions_root=actions_root,
        policy=PolicyRef(policy_id=policy.id, version=policy.version, definition_hash=policy.definition_hash()),
        decision=evaluation.decision,
        artifacts=artifacts,
        verification=verification,
        approvals=approvals,
        issued_at=now,
        receipt_id="rcpt-git-001",
    ).build_signed([issuer_key])

    return GitReceiptResult(
        receipt=receipt,
        decision=evaluation.decision,
        reasons=evaluation.reasons,
        changed_paths=changed_paths,
        before_commit=before_commit,
    )
