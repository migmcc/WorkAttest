from workattest.events import GENESIS, EventLog


def _log():
    log = EventLog()
    log.append("edit_file", "src/a.py", observed_by="git", occurred_at="2026-01-01T00:00:00Z")
    log.append("run_check", "tests", observed_by="verifier", occurred_at="2026-01-01T00:01:00Z")
    return log


def test_empty_head_is_genesis():
    assert EventLog().head == GENESIS


def test_chain_verifies():
    entries = _log().to_list()
    assert EventLog.verify_chain(entries) is True


def test_tamper_breaks_chain():  # THREAT-MODEL T-3
    entries = _log().to_list()
    entries[0]["resource"] = "src/evil.py"
    assert EventLog.verify_chain(entries) is False


def test_deleting_an_entry_breaks_chain():  # T-3
    entries = _log().to_list()
    del entries[0]
    assert EventLog.verify_chain(entries) is False


def test_reordering_breaks_chain():  # T-3
    entries = _log().to_list()
    entries.reverse()
    assert EventLog.verify_chain(entries) is False
