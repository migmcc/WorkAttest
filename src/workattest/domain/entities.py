"""Core domain entities.

Each entity is a frozen dataclass with a deterministic ``to_dict`` used for canonical
serialization. Field sets follow schemas/work-receipt.schema.json. Optional fields that
are ``None`` are omitted from ``to_dict`` so canonical output stays stable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from ..hashing import HashRef
from .enums import Decision, RiskClass, SubjectType, VerificationStatus


def _drop_none(data: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}


@dataclass(frozen=True)
class WorkRequest:
    id: str
    intent: str
    scope: str
    owner_subject: str
    risk_class: RiskClass
    created_at: str
    title: Optional[str] = None
    system: Optional[str] = None
    constraints: tuple[str, ...] = ()
    acceptance_criteria: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return _drop_none(
            {
                "id": self.id,
                "title": self.title,
                "intent": self.intent,
                "scope": self.scope,
                "owner_subject": self.owner_subject,
                "system": self.system,
                "risk_class": self.risk_class.value,
                "constraints": list(self.constraints),
                "acceptance_criteria": list(self.acceptance_criteria),
                "created_at": self.created_at,
            }
        )


@dataclass(frozen=True)
class Subject:
    id: str
    type: SubjectType
    public_key: str
    issuer: Optional[str] = None
    status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        return _drop_none(
            {
                "id": self.id,
                "type": self.type.value,
                "issuer": self.issuer,
                "public_key": self.public_key,
                "status": self.status,
            }
        )


@dataclass(frozen=True)
class Authorization:
    id: str
    request_id: str
    subject_id: str
    policy_id: str
    allowed_actions: tuple[str, ...]
    allowed_resources: tuple[str, ...]
    issued_at: str
    signature: Optional[dict[str, Any]] = None
    conditions: tuple[str, ...] = ()
    requires_approval: bool = False
    expires_at: Optional[str] = None
    revoked_at: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return _drop_none(
            {
                "id": self.id,
                "request_id": self.request_id,
                "subject_id": self.subject_id,
                "policy_id": self.policy_id,
                "allowed_actions": list(self.allowed_actions),
                "allowed_resources": list(self.allowed_resources),
                "conditions": list(self.conditions),
                "requires_approval": self.requires_approval,
                "issued_at": self.issued_at,
                "expires_at": self.expires_at,
                "revoked_at": self.revoked_at,
                "signature": self.signature,
            }
        )


@dataclass(frozen=True)
class ExecutionSession:
    id: str
    request_id: str
    authorization_id: str
    agent_subject_id: str
    human_owner_id: str
    started_at: str
    status: str = "running"
    model: Optional[str] = None
    configuration_hash: Optional[str] = None
    workspace: Optional[str] = None
    ended_at: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return _drop_none(
            {
                "id": self.id,
                "request_id": self.request_id,
                "authorization_id": self.authorization_id,
                "agent_subject_id": self.agent_subject_id,
                "human_owner_id": self.human_owner_id,
                "model": self.model,
                "configuration_hash": self.configuration_hash,
                "workspace": self.workspace,
                "started_at": self.started_at,
                "ended_at": self.ended_at,
                "status": self.status,
            }
        )


@dataclass(frozen=True)
class ArtifactEvidence:
    id: str
    path_or_uri: str
    source: str
    media_type: Optional[str] = None
    before_hash: Optional[HashRef] = None
    after_hash: Optional[HashRef] = None
    size: Optional[int] = None
    classification: Optional[str] = None
    evidence_uri: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return _drop_none(
            {
                "id": self.id,
                "path_or_uri": self.path_or_uri,
                "media_type": self.media_type,
                "before_hash": self.before_hash.to_dict() if self.before_hash else None,
                "after_hash": self.after_hash.to_dict() if self.after_hash else None,
                "size": self.size,
                "source": self.source,
                "classification": self.classification,
                "evidence_uri": self.evidence_uri,
            }
        )


@dataclass(frozen=True)
class VerificationResult:
    id: str
    check_id: str
    check_version: str
    definition_hash: HashRef
    status: VerificationStatus
    name: Optional[str] = None
    tool: Optional[str] = None
    tool_version: Optional[str] = None
    command: Optional[str] = None
    mandatory: bool = False
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    exit_code: Optional[int] = None
    output_hash: Optional[HashRef] = None
    evidence_refs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return _drop_none(
            {
                "id": self.id,
                "check_id": self.check_id,
                "name": self.name,
                "check_version": self.check_version,
                "definition_hash": self.definition_hash.to_dict(),
                "tool": self.tool,
                "tool_version": self.tool_version,
                "command": self.command,
                "mandatory": self.mandatory,
                "started_at": self.started_at,
                "ended_at": self.ended_at,
                "exit_code": self.exit_code,
                "status": self.status.value,
                "output_hash": self.output_hash.to_dict() if self.output_hash else None,
                "evidence_refs": list(self.evidence_refs),
            }
        )


@dataclass(frozen=True)
class ApprovalDecision:
    id: str
    execution_id: str
    approver_subject_id: str
    decision: str  # "approve" | "reject"
    result_hash: HashRef
    policy_id: str
    decided_at: str
    signature: Optional[dict[str, Any]] = None
    role: Optional[str] = None
    justification: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return _drop_none(
            {
                "id": self.id,
                "execution_id": self.execution_id,
                "approver_subject_id": self.approver_subject_id,
                "role": self.role,
                "decision": self.decision,
                "justification": self.justification,
                "result_hash": self.result_hash.to_dict(),
                "policy_id": self.policy_id,
                "decided_at": self.decided_at,
                "signature": self.signature,
            }
        )


@dataclass(frozen=True)
class PolicyRef:
    policy_id: str
    version: str
    definition_hash: HashRef
    uri: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return _drop_none(
            {
                "policy_id": self.policy_id,
                "version": self.version,
                "definition_hash": self.definition_hash.to_dict(),
                "uri": self.uri,
            }
        )
