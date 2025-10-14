"""Workflow engine handling OKR approval lifecycle."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Sequence
from uuid import uuid4

from ...services.access_policies import AccessContext, AccessDecision, ObjectRole, policy_engine


class WorkflowState(str, Enum):
    DRAFT = "draft"
    REVIEW = "expert_review"
    MANAGER_APPROVAL = "manager_approval"
    ACTIVE = "active"
    RETURNED = "returned"


@dataclass
class WorkflowHistoryEntry:
    timestamp: datetime
    action: str
    actor_id: str
    resulting_state: WorkflowState
    comment: str | None = None


@dataclass
class WorkflowInstance:
    id: str
    objective_id: str
    owner_id: str
    tenant_id: str
    workspace_ids: Sequence[str]
    state: WorkflowState = WorkflowState.DRAFT
    history: List[WorkflowHistoryEntry] = field(default_factory=list)

    def add_history(self, action: str, actor_id: str, state: WorkflowState, comment: str | None) -> None:
        self.history.append(
            WorkflowHistoryEntry(
                timestamp=datetime.now(timezone.utc),
                action=action,
                actor_id=actor_id,
                resulting_state=state,
                comment=comment,
            )
        )


class WorkflowEngine:
    """In-memory workflow state machine coordinating approvals."""

    transitions: Dict[WorkflowState, Dict[str, WorkflowState]] = {
        WorkflowState.DRAFT: {
            "workflow:submit": WorkflowState.REVIEW,
        },
        WorkflowState.REVIEW: {
            "workflow:return": WorkflowState.DRAFT,
            "workflow:review": WorkflowState.MANAGER_APPROVAL,
        },
        WorkflowState.MANAGER_APPROVAL: {
            "workflow:return": WorkflowState.REVIEW,
            "workflow:approve": WorkflowState.ACTIVE,
        },
        WorkflowState.ACTIVE: {
            "workflow:reopen": WorkflowState.RETURNED,
        },
        WorkflowState.RETURNED: {
            "workflow:submit": WorkflowState.REVIEW,
        },
    }

    def __init__(self) -> None:
        self._instances: Dict[str, WorkflowInstance] = {}

    def create_instance(
        self,
        objective_id: str,
        owner_id: str,
        tenant_id: str,
        workspace_ids: Sequence[str],
    ) -> WorkflowInstance:
        workflow_id = str(uuid4())
        instance = WorkflowInstance(
            id=workflow_id,
            objective_id=objective_id,
            owner_id=owner_id,
            tenant_id=tenant_id,
            workspace_ids=list(workspace_ids),
        )
        instance.add_history("workflow:create", owner_id, WorkflowState.DRAFT, "Workflow created")
        self._instances[workflow_id] = instance
        return instance

    def get_instance(self, workflow_id: str) -> WorkflowInstance | None:
        return self._instances.get(workflow_id)

    def list_instances(self) -> List[WorkflowInstance]:
        return list(self._instances.values())

    def advance(
        self,
        workflow_id: str,
        action: str,
        actor_context: AccessContext,
        comment: str | None = None,
        object_roles: Sequence[ObjectRole] | None = None,
    ) -> WorkflowInstance:
        instance = self.get_instance(workflow_id)
        if not instance:
            raise KeyError("Workflow not found")

        resource_attributes = {
            "id": instance.objective_id,
            "workspace_ids": list(instance.workspace_ids),
            "owner_id": instance.owner_id,
        }
        decision, permissions = policy_engine.is_action_allowed(
            user_id=actor_context.user_id,
            action=action,
            context=actor_context,
            resource_attributes=resource_attributes,
            object_roles=object_roles,
        )
        if decision is not AccessDecision.ALLOW:
            raise PermissionError(
                f"Action '{action}' not permitted for user {actor_context.user_id}. Permissions: {permissions}"
            )

        try:
            next_state = self.transitions[instance.state][action]
        except KeyError as exc:
            raise ValueError(
                f"Action '{action}' is not valid from state '{instance.state}'"
            ) from exc

        instance.state = next_state
        instance.add_history(action, actor_context.user_id, next_state, comment)
        return instance


workflow_engine = WorkflowEngine()
