"""In-memory directory backing SCIM endpoints."""
from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Dict, List
from uuid import uuid4

from .schemas import (
    SCIMEmail,
    SCIMGroup,
    SCIMGroupCreateRequest,
    SCIMGroupMember,
    SCIMUser,
    SCIMUserCreateRequest,
)


@dataclass
class DirectoryUser:
    id: str
    userName: str
    active: bool = True
    displayName: str | None = None
    name: dict | None = None
    emails: List[dict] = field(default_factory=list)
    externalId: str | None = None

    def to_api(self) -> SCIMUser:
        emails = [SCIMEmail(**email) for email in self.emails]
        return SCIMUser(
            id=self.id,
            userName=self.userName,
            active=self.active,
            displayName=self.displayName,
            name=self.name,
            emails=emails,
            externalId=self.externalId,
        )


@dataclass
class DirectoryGroup:
    id: str
    displayName: str
    members: List[SCIMGroupMember] = field(default_factory=list)

    def to_api(self) -> SCIMGroup:
        return SCIMGroup(id=self.id, displayName=self.displayName, members=self.members)


class InMemoryDirectory:
    """Thread-safe directory implementation used for the SCIM facade."""

    def __init__(self) -> None:
        self._users: Dict[str, DirectoryUser] = {}
        self._groups: Dict[str, DirectoryGroup] = {}
        self._lock = RLock()

    # -- User management ---------------------------------------------------
    def create_user(self, payload: SCIMUserCreateRequest) -> SCIMUser:
        with self._lock:
            user_id = str(uuid4())
            user = DirectoryUser(
                id=user_id,
                userName=payload.userName,
                active=payload.active,
                displayName=payload.displayName,
                name=payload.name.model_dump() if payload.name else None,
                emails=[email.model_dump() for email in payload.emails],
                externalId=payload.externalId,
            )
            self._users[user_id] = user
            return user.to_api()

    def list_users(self) -> List[SCIMUser]:
        with self._lock:
            return [user.to_api() for user in self._users.values()]

    def get_user(self, user_id: str) -> SCIMUser | None:
        with self._lock:
            user = self._users.get(user_id)
            return user.to_api() if user else None

    def replace_user(self, user_id: str, payload: SCIMUserCreateRequest) -> SCIMUser | None:
        with self._lock:
            if user_id not in self._users:
                return None
            user = DirectoryUser(
                id=user_id,
                userName=payload.userName,
                active=payload.active,
                displayName=payload.displayName,
                name=payload.name.model_dump() if payload.name else None,
                emails=[email.model_dump() for email in payload.emails],
                externalId=payload.externalId,
            )
            self._users[user_id] = user
            return user.to_api()

    def patch_user(self, user_id: str, operations: list[dict]) -> SCIMUser | None:
        with self._lock:
            user = self._users.get(user_id)
            if not user:
                return None
            for op in operations:
                operation = op.get("op", "").lower()
                path = op.get("path", "")
                value = op.get("value")
                if operation == "replace" and path.lower() == "active" and isinstance(value, bool):
                    user.active = value
                elif operation == "replace" and path.lower() == "displayname" and isinstance(value, str):
                    user.displayName = value
                elif operation == "replace" and path.lower() == "name" and isinstance(value, dict):
                    user.name = value
                elif operation == "replace" and path.lower() == "emails" and isinstance(value, list):
                    user.emails = value
            return user.to_api()

    def delete_user(self, user_id: str) -> bool:
        with self._lock:
            return self._users.pop(user_id, None) is not None

    # -- Group management --------------------------------------------------
    def create_group(self, payload: SCIMGroupCreateRequest) -> SCIMGroup:
        with self._lock:
            group_id = str(uuid4())
            group = DirectoryGroup(
                id=group_id,
                displayName=payload.displayName,
                members=payload.members,
            )
            self._groups[group_id] = group
            return group.to_api()

    def list_groups(self) -> List[SCIMGroup]:
        with self._lock:
            return [group.to_api() for group in self._groups.values()]

    def get_group(self, group_id: str) -> SCIMGroup | None:
        with self._lock:
            group = self._groups.get(group_id)
            return group.to_api() if group else None

    def replace_group(self, group_id: str, payload: SCIMGroupCreateRequest) -> SCIMGroup | None:
        with self._lock:
            if group_id not in self._groups:
                return None
            group = DirectoryGroup(id=group_id, displayName=payload.displayName, members=payload.members)
            self._groups[group_id] = group
            return group.to_api()

    def delete_group(self, group_id: str) -> bool:
        with self._lock:
            return self._groups.pop(group_id, None) is not None

    def add_member_to_group(self, group_id: str, member: SCIMGroupMember) -> SCIMGroup | None:
        with self._lock:
            group = self._groups.get(group_id)
            if not group:
                return None
            if member not in group.members:
                group.members.append(member)
            return group.to_api()

    def remove_member_from_group(self, group_id: str, member_id: str) -> SCIMGroup | None:
        with self._lock:
            group = self._groups.get(group_id)
            if not group:
                return None
            group.members = [m for m in group.members if m.value != member_id]
            return group.to_api()


directory = InMemoryDirectory()
