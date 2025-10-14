"""API router for the Workflow domain."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ...schemas.health import HealthStatus
from .schemas import (
    WorkflowActionRequest,
    WorkflowCreateRequest,
    WorkflowInstanceModel,
    WorkflowListResponse,
)
from .service import workflow_engine

router = APIRouter()


@router.get("/health", response_model=HealthStatus, status_code=status.HTTP_200_OK)
def healthcheck() -> HealthStatus:
    """Return a simple status payload for liveness probes."""

    return HealthStatus(status="ok", module="workflow")


@router.post("/instances", response_model=WorkflowInstanceModel, status_code=status.HTTP_201_CREATED)
def create_workflow(payload: WorkflowCreateRequest) -> WorkflowInstanceModel:
    """Create a new workflow instance for an objective."""

    instance = workflow_engine.create_instance(
        objective_id=payload.objective_id,
        owner_id=payload.owner_id,
        tenant_id=payload.tenant_id,
        workspace_ids=payload.workspace_ids,
    )
    return WorkflowInstanceModel.from_domain(instance)


@router.get("/instances", response_model=WorkflowListResponse)
def list_workflows() -> WorkflowListResponse:
    """List workflow instances currently tracked by the engine."""

    items = [WorkflowInstanceModel.from_domain(instance) for instance in workflow_engine.list_instances()]
    return WorkflowListResponse(items=items)


@router.get("/instances/{workflow_id}", response_model=WorkflowInstanceModel)
def get_workflow(workflow_id: str) -> WorkflowInstanceModel:
    """Fetch a specific workflow instance."""

    instance = workflow_engine.get_instance(workflow_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return WorkflowInstanceModel.from_domain(instance)


@router.post("/instances/{workflow_id}/actions", response_model=WorkflowInstanceModel)
def transition_workflow(workflow_id: str, payload: WorkflowActionRequest) -> WorkflowInstanceModel:
    """Execute a workflow transition after validating access policies."""

    context = payload.context.to_domain()
    try:
        instance = workflow_engine.advance(
            workflow_id=workflow_id,
            action=payload.action,
            actor_context=context,
            comment=payload.comment,
            object_roles=payload.object_roles,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return WorkflowInstanceModel.from_domain(instance)
