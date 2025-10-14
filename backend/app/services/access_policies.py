"""RBAC and ABAC policy helpers."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class ObjectRole(str, Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    APPROVER = "approver"


@dataclass(frozen=True)
class AccessContext:
    user_id: str
    tenant_id: str
    workspace_ids: frozenset[str]
    manager_of: frozenset[str]
    labels: frozenset[str]
    ad_groups: frozenset[str]
    level: str | None = None


def can_view_object(context: AccessContext, object_workspace_id: str, owner_id: str) -> bool:
    """Evaluate cross-cutting ABAC rules for view permissions."""

    if owner_id == context.user_id:
        return True

    if object_workspace_id in context.workspace_ids:
        return True

    if owner_id in context.manager_of:
        return True

    return False


def can_edit_object(
    context: AccessContext,
    object_workspace_id: str,
    owner_id: str,
    object_roles: Iterable[ObjectRole],
) -> bool:
    """Evaluate edit permissions across ABAC and object-level roles."""

    if ObjectRole.EDITOR in object_roles or ObjectRole.APPROVER in object_roles:
        return True

    return owner_id in context.manager_of and object_workspace_id in context.workspace_ids
