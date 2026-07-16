import pytest

from workattest.domain.entities import (
    ApprovalDecision,
    Authorization,
    VerificationResult,
    WorkRequest,
)
from workattest.domain.enums import Decision, RiskClass, VerificationStatus
from workattest.hashing import hash_canonical
from workattest.policy import Policy, evaluate

NOW = "2026-01-01T00:00:00Z"
RESULT_HASH = hash_canonical({"result": "x"})


def _request(risk=RiskClass.LOW):
    return WorkRequest(
        id="req", intent="fix", scope="src", owner_subject="human",
        risk_class=risk, created_at=NOW,
    )


def _auth(**kw):
    base = dict(
        id="auth", request_id="req", subject_id="agent", policy_id="pol",
        allowed_actions=("edit_file",), allowed_resources=("src/a.py",), issued_at=NOW,
    )
    base.update(kw)
    return Authorization(**base)


def _passed_check(check_id="tests"):
    return VerificationResult(
        id="vr", check_id=check_id, check_version="1", definition_hash=hash_canonical({"c": check_id}),
        status=VerificationStatus.PASSED, mandatory=True,
    )


def _eval(**kw):
    base = dict(
        request=_request(), authorization=_auth(), policy=Policy("pol", "1"),
        execution_id="exec", result_hash=RESULT_HASH, now=NOW,
        observed_actions=("edit_file",), observed_resources=("src/a.py",),
    )
    base.update(kw)
    return evaluate(**base)


def test_accept_when_all_satisfied():
    assert _eval().decision is Decision.ACCEPT


def test_refuse_when_action_out_of_scope():  # INV-3
    ev = _eval(observed_actions=("delete_repo",))
    assert ev.decision is Decision.REFUSE
    assert any("outside the authorized scope" in r for r in ev.reasons)


def test_refuse_when_resource_out_of_scope():  # T-8
    ev = _eval(observed_resources=("/etc/passwd",))
    assert ev.decision is Decision.REFUSE


def test_refuse_when_expired():  # T-7
    ev = _eval(authorization=_auth(expires_at="2020-01-01T00:00:00Z"))
    assert ev.decision is Decision.REFUSE
    assert any("expired" in r for r in ev.reasons)


def test_refuse_when_revoked():
    ev = _eval(authorization=_auth(revoked_at=NOW))
    assert ev.decision is Decision.REFUSE


def test_hold_when_mandatory_check_missing():  # INV-8 / T-5
    ev = _eval(policy=Policy("pol", "1", mandatory_check_ids=("tests",)), verification_results=())
    assert ev.decision is Decision.HOLD
    assert any("did not run" in r for r in ev.reasons)


def test_hold_when_mandatory_check_failed():  # INV-8
    failed = VerificationResult(
        id="vr", check_id="tests", check_version="1", definition_hash=hash_canonical({"c": "t"}),
        status=VerificationStatus.FAILED, mandatory=True,
    )
    ev = _eval(policy=Policy("pol", "1", mandatory_check_ids=("tests",)), verification_results=(failed,))
    assert ev.decision is Decision.HOLD


def test_hold_when_high_risk_without_approval():  # INV-16
    ev = _eval(request=_request(RiskClass.HIGH), approvals=())
    assert ev.decision is Decision.HOLD


def test_accept_when_high_risk_with_bound_approval():
    approval = ApprovalDecision(
        id="apr", execution_id="exec", approver_subject_id="human", decision="approve",
        result_hash=RESULT_HASH, policy_id="pol", decided_at=NOW,
    )
    ev = _eval(request=_request(RiskClass.HIGH), approvals=(approval,))
    assert ev.decision is Decision.ACCEPT


def test_hold_when_approval_from_other_execution():  # INV-9 / T-6
    approval = ApprovalDecision(
        id="apr", execution_id="OTHER-exec", approver_subject_id="human", decision="approve",
        result_hash=RESULT_HASH, policy_id="pol", decided_at=NOW,
    )
    ev = _eval(request=_request(RiskClass.HIGH), approvals=(approval,))
    assert ev.decision is Decision.HOLD


def test_determinism_same_inputs_same_output():  # NFR-1
    assert _eval() == _eval()


def test_policy_definition_hash_stable():
    p = Policy("pol", "1", mandatory_check_ids=("b", "a"))
    assert p.definition_hash() == Policy("pol", "1", mandatory_check_ids=("a", "b")).definition_hash()
