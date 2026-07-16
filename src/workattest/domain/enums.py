"""Domain enumerations."""

from __future__ import annotations

from enum import Enum


class Decision(str, Enum):
    """Terminal policy decision (ACCOUNTABILITY-MODEL §4)."""

    ACCEPT = "ACCEPT"
    HOLD = "HOLD"
    REFUSE = "REFUSE"


class RiskClass(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def requires_human_approval(self) -> bool:
        """High-impact actions require human approval (INV-16)."""
        return self in (RiskClass.HIGH, RiskClass.CRITICAL)


class SubjectType(str, Enum):
    HUMAN = "human"
    AGENT = "agent"
    SERVICE_ACCOUNT = "service_account"
    WORKLOAD = "workload"
    TOOL = "tool"
    ORGANIZATION = "organization"


class VerificationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
