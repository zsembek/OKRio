from datetime import datetime, timezone

from app.modules.workflow.schemas import WorkflowHistoryEntryModel, WorkflowInstanceModel
from app.modules.workflow.service import WorkflowHistoryEntry, WorkflowInstance, WorkflowState


def test_workflow_instance_model_from_domain():
    history_entry = WorkflowHistoryEntry(
        timestamp=datetime.now(timezone.utc),
        action="workflow:create",
        actor_id="user-1",
        resulting_state=WorkflowState.DRAFT,
        comment="initial",
    )
    instance = WorkflowInstance(
        id="wf-1",
        objective_id="obj-1",
        owner_id="user-1",
        tenant_id="tenant-1",
        workspace_ids=["ws-1"],
    )
    instance.history.append(history_entry)

    model = WorkflowInstanceModel.from_domain(instance)

    assert model.id == "wf-1"
    assert model.state == WorkflowState.DRAFT
    assert model.history[0].action == "workflow:create"
    assert model.history[0].timestamp == history_entry.timestamp


def test_workflow_history_entry_model_from_domain():
    history_entry = WorkflowHistoryEntry(
        timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
        action="workflow:approve",
        actor_id="manager-1",
        resulting_state=WorkflowState.ACTIVE,
        comment="approved",
    )

    model = WorkflowHistoryEntryModel.from_domain(history_entry)

    assert model.resulting_state == WorkflowState.ACTIVE
    assert model.comment == "approved"
    assert model.actor_id == "manager-1"
