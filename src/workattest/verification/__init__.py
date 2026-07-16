"""Verifier — run operator-defined checks and attest their real results.

The agent never selects the checks that verify it (INV-5): a :class:`Check` comes from an
operator/organization config, is identified by a hash of its definition (INV-7), and its
result records the real exit code, output hash and timing. Absence or failure of a
mandatory check can never yield ACCEPT (INV-8).
"""

from .runner import Check, load_checks, run_check, run_checks

__all__ = ["Check", "run_check", "run_checks", "load_checks"]
