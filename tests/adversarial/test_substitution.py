"""Adversarial tests — substituting a declaration for the real thing.

These two attacks do not tamper with receipt bytes (that is `test_tamper.py`). They try to
make the system record work that never happened:

* **T-4** the agent declares a check as passed without running it;
* **T-9** the policy is swapped for a weaker one without updating its hash.

Both are defended by the same principle: what is recorded is derived from execution and
from definitions, never from a claim.
"""

from __future__ import annotations

import sys

from workattest.domain.entities import Authorization, WorkRequest
from workattest.domain.enums import Decision, RiskClass, VerificationStatus
from workattest.hashing import hash_canonical
from workattest.policy import Policy, evaluate
from workattest.verification.runner import Check, run_check


# --------------------------------------------------------------------------- T-4


def _check(check_id: str, command: tuple[str, ...], *, mandatory: bool = True) -> Check:
    return Check(id=check_id, command=command, mandatory=mandatory, tool="python")


def test_t4_a_failing_check_cannot_be_recorded_as_passed(tmp_path):
    """The status is derived from the real exit code, not from anything declared."""
    failing = _check("tests", (sys.executable, "-c", "raise SystemExit(1)"))
    result = run_check(failing, tmp_path)

    assert result.status is VerificationStatus.FAILED
    assert result.exit_code == 1


def test_t4_a_check_that_cannot_launch_is_an_error_not_a_pass(tmp_path):
    """An absent tool must not silently read as success."""
    missing = _check("tests", ("this-binary-does-not-exist-workattest",))
    result = run_check(missing, tmp_path)

    assert result.status is VerificationStatus.ERROR
    assert result.status is not VerificationStatus.PASSED


def test_t4_declared_check_is_not_the_operator_check(tmp_path):
    """Swapping the command for a trivially-passing one changes the definition hash.

    An agent that substitutes `exit 0` for the operator's real test command produces a
    result that no longer matches the operator's check definition, so the substitution is
    detectable by comparing hashes — the agent does not get to choose the checks (INV-5).
    """
    operator_check = _check("tests", (sys.executable, "-m", "pytest", "-q"))
    agent_substitute = _check("tests", (sys.executable, "-c", "pass"))

    assert operator_check.id == agent_substitute.id
    assert operator_check.definition_hash() != agent_substitute.definition_hash()

    passing = run_check(agent_substitute, tmp_path)
    assert passing.status is VerificationStatus.PASSED
    assert passing.definition_hash != operator_check.definition_hash()


def test_t4_mandatory_failed_check_forces_hold(tmp_path):
    """A failed mandatory check must close to HOLD, never ACCEPT (INV-8, INV-20).

    This is the end of the T-4 chain: even if an agent claims the work is done, the
    recorded status comes from the process that actually ran, and a mandatory failure
    cannot reach ACCEPT.
    """
    now = "2026-01-01T00:00:00Z"
    failed = run_check(_check("tests", (sys.executable, "-c", "raise SystemExit(1)")), tmp_path)

    evaluation = evaluate(
        request=WorkRequest(
            id="req", intent="fix", scope="src", owner_subject="human",
            risk_class=RiskClass.LOW, created_at=now,
        ),
        authorization=Authorization(
            id="auth", request_id="req", subject_id="agent", policy_id="pol",
            allowed_actions=("edit_file",), allowed_resources=("src/a.py",), issued_at=now,
        ),
        policy=Policy("pol", "1", mandatory_check_ids=("tests",)),
        execution_id="exec",
        result_hash=hash_canonical({"result": "x"}),
        verification_results=[failed],
        observed_actions=("edit_file",),
        observed_resources=("src/a.py",),
        now=now,
    )

    assert evaluation.decision is not Decision.ACCEPT
    assert evaluation.decision is Decision.HOLD


# --------------------------------------------------------------------------- T-9


def test_t9_weakening_a_policy_changes_its_definition_hash():
    """Dropping a mandatory check produces a different policy hash."""
    strict = Policy(id="pol-swchange", version="1.0.0", mandatory_check_ids=("tests", "lint"))
    weakened = Policy(id="pol-swchange", version="1.0.0", mandatory_check_ids=("lint",))

    # Same id and version — only the substance changed.
    assert strict.id == weakened.id
    assert strict.version == weakened.version
    assert strict.definition_hash() != weakened.definition_hash()


def test_t9_substituted_policy_does_not_match_the_recorded_hash():
    """A receipt recording the strict hash cannot have been evaluated by the weak policy."""
    strict = Policy(id="pol-swchange", version="1.0.0", mandatory_check_ids=("tests", "lint"))
    weakened = Policy(id="pol-swchange", version="1.0.0", mandatory_check_ids=("lint",))

    recorded_in_receipt = strict.definition_hash()
    assert weakened.definition_hash() != recorded_in_receipt


def test_t9_policy_hash_is_stable_for_the_same_definition():
    """The detection above is only meaningful if the hash is otherwise deterministic."""
    a = Policy(id="pol-swchange", version="1.0.0", mandatory_check_ids=("tests", "lint"))
    b = Policy(id="pol-swchange", version="1.0.0", mandatory_check_ids=("tests", "lint"))
    assert a.definition_hash() == b.definition_hash()
