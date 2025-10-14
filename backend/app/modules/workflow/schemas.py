"""Pydantic models for workflow operations."""
from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from ...services.access_policies import ObjectRole
from ..auth.schemas import AccessContextModel
from .service import WorkflowHistoryEntry, WorkflowInstance, WorkflowState


class WorkflowCreateRequest(BaseModel):
    objective_id: str
    owner_id: str
    tenant_id: str
    workspace_ids: List[str]


class WorkflowActionRequest(BaseModel):
    action: str = Field(..., description="Action to perform (workflow:submit, workflow:approve, etc.)")
    context: AccessContextModel
    comment: str | None = None
    object_roles: List[ObjectRole] | None = None


class WorkflowHistoryEntryModel(BaseModel):
    timestamp: datetime
    action: str
    actor_id: str
    resulting_state: WorkflowState
    comment: str | None = None

    @classmethod
    def from_domain(cls, entry: WorkflowHistoryEntry) -> "WorkflowHistoryEntryModel":
        return cls(
            timestamp=entry.timestamp,
            action=entry.action,
            actor_id=entry.actor_id,
            resulting_state=entry.resulting_state,
            comment=entry.comment,
        )


class WorkflowInstanceModel(BaseModel):
    id: str
    objective_id: str
    owner_id: str
    tenant_id: str
    workspace_ids: List[str]
    state: WorkflowState
    history: List[WorkflowHistoryEntryModel]

    @classmethod
    def from_domain(cls, instance: WorkflowInstance) -> "WorkflowInstanceModel":
        return cls(
            id=instance.id,
            objective_id=instance.objective_id,
            owner_id=instance.owner_id,
            tenant_id=instance.tenant_id,
            workspace_ids=list(instance.workspace_ids),
            state=instance.state,
            history=[WorkflowHistoryEntryModel.from_domain(entry) for entry in instance.history],
        )


class WorkflowListResponse(BaseModel):
    items: List[WorkflowInstanceModel]
