"""WorkAttest core domain.

Entities, enums and invariants. The domain is deterministic and independent of any
infrastructure (no FastAPI, GitHub, Claude, Codex or database) — NFR-2.
"""

from .enums import Decision, RiskClass, SubjectType, VerificationStatus
from .entities import (
    ApprovalDecision,
    ArtifactEvidence,
    Authorization,
    ExecutionSession,
    PolicyRef,
    Subject,
    VerificationResult,
    WorkRequest,
)

__all__ = [
    "Decision",
    "RiskClass",
    "SubjectType",
    "VerificationStatus",
    "WorkRequest",
    "Subject",
    "Authorization",
    "ExecutionSession",
    "ArtifactEvidence",
    "VerificationResult",
    "ApprovalDecision",
    "PolicyRef",
]
