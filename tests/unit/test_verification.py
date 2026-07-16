import sys

from workattest.domain.enums import VerificationStatus
from workattest.verification import Check, run_check, run_checks


def _py(code: str) -> tuple[str, ...]:
    return (sys.executable, "-c", code)


def test_passing_check():
    vr = run_check(Check(id="ok", command=_py("import sys; sys.exit(0)")), cwd=".")
    assert vr.status is VerificationStatus.PASSED
    assert vr.exit_code == 0
    assert vr.check_id == "ok"
    assert vr.output_hash is not None


def test_failing_check():
    vr = run_check(Check(id="bad", command=_py("import sys; sys.exit(3)")), cwd=".")
    assert vr.status is VerificationStatus.FAILED
    assert vr.exit_code == 3


def test_launch_error_is_error_status():
    vr = run_check(Check(id="nope", command=("this-binary-does-not-exist-xyz",)), cwd=".")
    assert vr.status is VerificationStatus.ERROR


def test_timeout_is_error_status():
    vr = run_check(Check(id="slow", command=_py("import time; time.sleep(5)"), timeout_s=1), cwd=".")
    assert vr.status is VerificationStatus.ERROR


def test_definition_hash_is_stable_and_content_sensitive():
    a = Check(id="c", command=("x", "y"))
    b = Check(id="c", command=("x", "y"))
    c = Check(id="c", command=("x", "z"))
    assert a.definition_hash() == b.definition_hash()
    assert a.definition_hash() != c.definition_hash()


def test_output_hash_reflects_output():
    vr1 = run_check(Check(id="o", command=_py("print('hello')")), cwd=".")
    vr2 = run_check(Check(id="o", command=_py("print('world')")), cwd=".")
    assert vr1.output_hash != vr2.output_hash


def test_run_checks_preserves_order():
    checks = [Check(id="a", command=_py("pass")), Check(id="b", command=_py("pass"))]
    results = run_checks(checks, cwd=".")
    assert [r.check_id for r in results] == ["a", "b"]
