"""Deterministic policy engine → ACCEPT / HOLD / REFUSE.

Determinism is a hard requirement (NFR-1): the same inputs always yield the same
decision and the same ordered reasons. The policy is versioned and hashable (INV-7) so
the exact rules that produced a decision are provable.

Decision precedence (highest first):
1. REFUSE — a hard violation: revoked/expired authorization, action or resource
   outside the authorized scope, or subject mismatch (INV-3).
2. HOLD — recoverable: a mandatory check missing/not-passed (INV-8), or required human
   approval absent or not bound to this execution's result (INV-9, INV-16).
3. ACCEPT — all gates satisfied.

Fail-safe (INV-20): any ambiguity or missing input resolves away from ACCEPT.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from ..domain.entities import (
    ApprovalDecision,
    Authorization,
    VerificationResult,
    WorkRequest,
)
from ..domain.enums import Decision, RiskClass, VerificationStatus
from ..hashing import HashRef, hash_canonical


@dataclass(frozen=True)
class Policy:
    id: str
    version: str
    mandatory_check_ids: tuple[str, ...] = ()

    def definition(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "mandatory_check_ids": sorted(self.mandatory_check_ids),
        }

    def definition_hash(self) -> HashRef:
        return hash_canonical(self.definition())


@dataclass(frozen=True)
class PolicyEvaluation:
    decision: Decision
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"decision": self.decision.value, "reasons": list(self.reasons)}


def _authorization_refusals(
    request: WorkRequest,
    authorization: Authorization,
    observed_actions: Sequence[str],
    observed_resources: Sequence[str],
    now: str,
) -> list[str]:
    reasons: list[str] = []
    if authorization.request_id != request.id:
        reasons.append("authorization does not match the work request (INV-1/INV-3)")
    if not authorization.subject_id:
        reasons.append("authorization has no subject (INV-2)")
    if authorization.revoked_at is not None:
        reasons.append("authorization is revoked")
    if authorization.expires_at is not None and now > authorization.expires_at:
        reasons.append("authorization is expired")
    allowed_actions = set(authorization.allowed_actions)
    for action in sorted(set(observed_actions)):
        if action not in allowed_actions:
            reasons.append(f"action '{action}' is outside the authorized scope (INV-3)")
    for resource in sorted(set(observed_resources)):
        if not _resource_allowed(resource, authorization.allowed_resources):
            reasons.append(f"resource '{resource}' is outside the authorized scope (INV-3)")
    return reasons


def _resource_allowed(resource: str, allowed: Sequence[str]) -> bool:
    """Match a resource against authorized entries.

    An entry may be an exact path, or a directory-scope pattern ending in ``/`` or
    ``/**`` that matches any resource beneath that directory. Matching is prefix-based
    on path segments, so ``src/`` allows ``src/a.py`` but not ``src-other/a.py``.
    """
    for entry in allowed:
        if entry == resource:
            return True
        prefix = None
        if entry.endswith("/**"):
            prefix = entry[:-2]  # keep trailing slash
        elif entry.endswith("/"):
            prefix = entry
        if prefix is not None and resource.startswith(prefix):
            return True
    return False


def _check_holds(
    policy: Policy, verification_results: Sequence[VerificationResult]
) -> list[str]:
    reasons: list[str] = []
    by_id: dict[str, VerificationResult] = {}
    for vr in verification_results:
        # A later result for the same check id supersedes an earlier one deterministically
        by_id[vr.check_id] = vr
    for check_id in sorted(policy.mandatory_check_ids):
        vr = by_id.get(check_id)
        if vr is None:
            reasons.append(f"mandatory check '{check_id}' did not run (INV-8)")
        elif vr.status is not VerificationStatus.PASSED:
            reasons.append(
                f"mandatory check '{check_id}' status is {vr.status.value}, not passed (INV-8)"
            )
    return reasons


def _approval_holds(
    request: WorkRequest,
    authorization: Authorization,
    execution_id: str,
    result_hash: HashRef,
    approvals: Sequence[ApprovalDecision],
    policy: Policy,
) -> list[str]:
    needs_approval = authorization.requires_approval or request.risk_class.requires_human_approval
    if not needs_approval:
        return []
    for ap in approvals:
        if ap.decision != "approve":
            continue
        if ap.execution_id != execution_id:
            # An approval can only accept the result of the SAME execution (INV-9).
            continue
        if ap.result_hash != result_hash:
            continue
        if ap.policy_id != policy.id:
            continue
        return []  # a valid, binding approval exists
    return ["required human approval is missing or not bound to this result (INV-9/INV-16)"]


def evaluate(
    *,
    request: WorkRequest,
    authorization: Authorization,
    policy: Policy,
    execution_id: str,
    result_hash: HashRef,
    verification_results: Sequence[VerificationResult] = (),
    approvals: Sequence[ApprovalDecision] = (),
    observed_actions: Sequence[str] = (),
    observed_resources: Sequence[str] = (),
    now: str,
) -> PolicyEvaluation:
    """Evaluate the policy deterministically and return a decision with ordered reasons."""
    refuse_reasons = _authorization_refusals(
        request, authorization, observed_actions, observed_resources, now
    )
    if refuse_reasons:
        return PolicyEvaluation(Decision.REFUSE, tuple(refuse_reasons))

    hold_reasons = _check_holds(policy, verification_results)
    hold_reasons += _approval_holds(
        request, authorization, execution_id, result_hash, approvals, policy
    )
    if hold_reasons:
        return PolicyEvaluation(Decision.HOLD, tuple(hold_reasons))

    return PolicyEvaluation(Decision.ACCEPT, ("all authorized, verified and approved",))
