"""Adapters connect the deterministic core to real systems.

Adapters observe or mediate the systems affected by work (Git, filesystem, ...). They
collect facts from the affected system itself — never from the agent's self-report
(INV-4, TRUST-BOUNDARIES boundary #1).
"""
