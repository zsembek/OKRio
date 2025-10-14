"""Comprehensive RBAC, ABAC, and object-role policy helpers.

This module centralises access control logic for the OKRio backend. It
supports:

* **Role-based access control (RBAC)** via named role definitions and
  permission grants.
* **Attribute-based access control (ABAC)** using declarative conditions
  that inspect the caller context and resource metadata.
* **Object roles** that attach fine-grained capabilities to a specific
  resource instance (e.g., objective approver).

The implementation is intentionally framework-agnostic so it can be reused in
FastAPI dependencies, background tasks, or even external workers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, Mapping, MutableMapping, Sequence, Set


class ObjectRole(str, Enum):
    """Enumerates object-level roles exposed to tenants."""

    VIEWER = "viewer"
    EDITOR = "editor"
    APPROVER = "approver"


class AccessDecision(str, Enum):
    """Decision outcomes returned by the policy engine."""

    ALLOW = "allow"
    DENY = "deny"


class ConditionOperator(str, Enum):
    """Supported operators for attribute conditions."""

    ANY = "any"
    CONTAINS = "contains"
    MATCH_RESOURCE = "match_resource"
    EQUALS = "equals"


@dataclass(frozen=True)
class AccessContext:
    """Runtime attributes about the caller used for ABAC evaluation."""

    user_id: str
    tenant_id: str
    workspace_ids: frozenset[str] = field(default_factory=frozenset)
    manager_of: frozenset[str] = field(default_factory=frozenset)
    labels: frozenset[str] = field(default_factory=frozenset)
    ad_groups: frozenset[str] = field(default_factory=frozenset)
    level: str | None = None
    attributes: Mapping[str, Sequence[str] | str] = field(default_factory=dict)


@dataclass(frozen=True)
class AttributeCondition:
    """Declarative ABAC rule bound to a role definition."""

    attribute: str
    operator: ConditionOperator
    values: frozenset[str] = field(default_factory=frozenset)
    resource_attribute: str | None = None

    def evaluate(
        self,
        context: AccessContext,
        resource_attributes: Mapping[str, Sequence[str] | str] | None = None,
    ) -> bool:
        """Return ``True`` if the context satisfies the condition."""

        resource_attributes = resource_attributes or {}
        context_value = _coerce_to_set(_get_context_attribute(context, self.attribute))

        if self.operator is ConditionOperator.ANY:
            return bool(context_value)

        if self.operator is ConditionOperator.EQUALS:
            return bool(context_value) and context_value == self.values

        if self.operator is ConditionOperator.CONTAINS:
            return bool(context_value.intersection(self.values))

        if self.operator is ConditionOperator.MATCH_RESOURCE:
            if not self.resource_attribute:
                return False
            resource_value = _coerce_to_set(resource_attributes.get(self.resource_attribute, set()))
            return bool(context_value.intersection(resource_value))

        return False


@dataclass(frozen=True)
class RoleDefinition:
    """RBAC role with optional ABAC conditions and implied roles."""

    name: str
    permissions: frozenset[str]
    conditions: tuple[AttributeCondition, ...] = ()
    implied_roles: frozenset[str] = field(default_factory=frozenset)


class AccessPolicyEngine:
    """Runtime engine used to manage RBAC/ABAC/object-role state."""

    def __init__(self) -> None:
        self._roles: Dict[str, RoleDefinition] = {}
        self._role_assignments: MutableMapping[str, Set[str]] = {}
        self._object_roles: MutableMapping[tuple[str, str], Set[ObjectRole]] = {}
        self._object_role_permissions: MutableMapping[ObjectRole, Set[str]] = {
            ObjectRole.VIEWER: {"workflow:view", "okr:view"},
            ObjectRole.EDITOR: {"workflow:view", "workflow:edit", "okr:edit"},
            ObjectRole.APPROVER: {"workflow:view", "workflow:approve"},
        }

    # -- Role registration -------------------------------------------------
    def register_role(self, role: RoleDefinition) -> None:
        """Register or overwrite a role definition."""

        self._roles[role.name] = role

    def describe_roles(self) -> list[RoleDefinition]:
        """Return all registered role definitions."""

        return list(self._roles.values())

    # -- Role assignments --------------------------------------------------
    def assign_role(self, user_id: str, role_name: str) -> None:
        """Assign a role to a user."""

        if role_name not in self._roles:
            raise KeyError(f"Unknown role '{role_name}'")
        self._role_assignments.setdefault(user_id, set()).add(role_name)

    def revoke_role(self, user_id: str, role_name: str) -> None:
        """Remove a role from a user."""

        if user_id in self._role_assignments:
            self._role_assignments[user_id].discard(role_name)
            if not self._role_assignments[user_id]:
                del self._role_assignments[user_id]

    def get_assignments(self, user_id: str) -> set[str]:
        """Return a copy of assigned role names."""

        return set(self._role_assignments.get(user_id, set()))

    # -- Object role management -------------------------------------------
    def grant_object_role(self, user_id: str, object_id: str, role: ObjectRole) -> None:
        """Grant an object-level role to a user for a resource."""

        self._object_roles.setdefault((object_id, user_id), set()).add(role)

    def revoke_object_role(self, user_id: str, object_id: str, role: ObjectRole) -> None:
        """Revoke an object-level role assignment."""

        key = (object_id, user_id)
        if key in self._object_roles:
            self._object_roles[key].discard(role)
            if not self._object_roles[key]:
                del self._object_roles[key]

    def configure_object_role_permissions(
        self, role: ObjectRole, permissions: Iterable[str]
    ) -> None:
        """Override permissions granted by an object-level role."""

        self._object_role_permissions[role] = set(permissions)

    def _permissions_from_object_roles(
        self, object_roles: Iterable[ObjectRole]
    ) -> set[str]:
        permissions: set[str] = set()
        for role in object_roles:
            permissions.update(self._object_role_permissions.get(role, set()))
        return permissions

    # -- Evaluation --------------------------------------------------------
    def is_action_allowed(
        self,
        user_id: str,
        action: str,
        context: AccessContext,
        resource_attributes: Mapping[str, Sequence[str] | str] | None = None,
        object_roles: Iterable[ObjectRole] | None = None,
    ) -> tuple[AccessDecision, set[str]]:
        """Evaluate the supplied action and return the decision + permissions."""

        resource_attributes = resource_attributes or {}
        effective_permissions = self._collect_permissions(
            user_id=user_id, context=context, resource_attributes=resource_attributes
        )

        combined_permissions = set(effective_permissions)

        if object_roles is None:
            object_roles = self._object_roles.get((resource_attributes.get("id", ""), user_id), set())

        if object_roles:
            combined_permissions.update(self._permissions_from_object_roles(object_roles))

        if action in combined_permissions:
            return AccessDecision.ALLOW, combined_permissions
        return AccessDecision.DENY, combined_permissions

    def _collect_permissions(
        self,
        user_id: str,
        context: AccessContext,
        resource_attributes: Mapping[str, Sequence[str] | str],
    ) -> set[str]:
        permissions: set[str] = set()
        visited: set[str] = set()
        for role_name in self._role_assignments.get(user_id, set()):
            permissions.update(
                self._resolve_permissions(
                    role_name=role_name,
                    visited=visited,
                    context=context,
                    resource_attributes=resource_attributes,
                )
            )
        return permissions

    def _resolve_permissions(
        self,
        role_name: str,
        visited: set[str],
        context: AccessContext,
        resource_attributes: Mapping[str, Sequence[str] | str],
    ) -> set[str]:
        if role_name in visited:
            return set()

        visited.add(role_name)
        role = self._roles.get(role_name)
        if role is None:
            return set()

        if not all(condition.evaluate(context, resource_attributes) for condition in role.conditions):
            return set()

        permissions = set(role.permissions)
        for implied in role.implied_roles:
            permissions.update(
                self._resolve_permissions(
                    role_name=implied,
                    visited=visited,
                    context=context,
                    resource_attributes=resource_attributes,
                )
            )
        return permissions


def _get_context_attribute(context: AccessContext, attribute: str) -> Sequence[str] | str | None:
    if hasattr(context, attribute):
        return getattr(context, attribute)
    return context.attributes.get(attribute) if isinstance(context.attributes, Mapping) else None


def _coerce_to_set(value: Sequence[str] | str | None) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        return {value}
    return set(value)


# Backwards-compatible helper utilities ------------------------------------

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


# Default role catalogue ----------------------------------------------------

policy_engine = AccessPolicyEngine()

policy_engine.register_role(
    RoleDefinition(
        name="global_admin",
        permissions=frozenset(
            {
                "workflow:create",
                "workflow:edit",
                "workflow:approve",
                "workflow:view",
                "workflow:submit",
                "workflow:return",
                "workflow:review",
                "workflow:reopen",
                "scim:manage",
                "roles:assign",
            }
        ),
        conditions=(),
    )
)

policy_engine.register_role(
    RoleDefinition(
        name="workspace_owner",
        permissions=frozenset({"workflow:view", "workflow:edit", "workflow:submit"}),
        conditions=(
            AttributeCondition(
                attribute="workspace_ids",
                operator=ConditionOperator.MATCH_RESOURCE,
                resource_attribute="workspace_ids",
            ),
        ),
    )
)

policy_engine.register_role(
    RoleDefinition(
        name="okr_expert",
        permissions=frozenset({"workflow:view", "workflow:review", "workflow:return"}),
        conditions=(
            AttributeCondition(
                attribute="labels",
                operator=ConditionOperator.CONTAINS,
                values=frozenset({"okr-expert"}),
            ),
        ),
    )
)

policy_engine.register_role(
    RoleDefinition(
        name="manager",
        permissions=frozenset({"workflow:view", "workflow:approve", "workflow:return"}),
        conditions=(
            AttributeCondition(
                attribute="manager_of",
                operator=ConditionOperator.MATCH_RESOURCE,
                resource_attribute="owner_id",
            ),
        ),
    )
)
