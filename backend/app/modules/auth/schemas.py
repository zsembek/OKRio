"""Pydantic schemas for the Auth module."""
from __future__ import annotations

from typing import List, Sequence

from pydantic import BaseModel, Field

from ...services.access_policies import AccessDecision, AccessContext, ObjectRole


class AzureOAuthAuthorizeRequest(BaseModel):
    state: str = Field(..., description="Opaque state to prevent CSRF attacks")
    nonce: str | None = Field(None, description="Nonce propagated to the ID token")
    scopes: List[str] | None = Field(None, description="Optional scope override")
    redirect_uri: str | None = Field(None, description="Explicit redirect URI override")
    code_challenge: str | None = Field(None, description="Precomputed PKCE challenge")
    code_challenge_method: str | None = Field(
        None,
        description="PKCE challenge method (defaults to S256)",
    )


class AzureOAuthAuthorizeResponse(BaseModel):
    authorization_url: str
    code_verifier: str | None = Field(None, description="Verifier used to complete PKCE flow")


class AzureOAuthTokenRequest(BaseModel):
    code: str
    redirect_uri: str
    code_verifier: str | None = None


class AzureOAuthTokenResponse(BaseModel):
    token_type: str
    scope: str
    expires_in: int
    ext_expires_in: int | None = None
    access_token: str
    refresh_token: str | None = None
    id_token: str | None = None


class AzureOAuthRefreshRequest(BaseModel):
    refresh_token: str


class AzureLogoutResponse(BaseModel):
    logout_url: str


class AccessContextModel(BaseModel):
    user_id: str
    tenant_id: str
    workspace_ids: List[str] = Field(default_factory=list)
    manager_of: List[str] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    ad_groups: List[str] = Field(default_factory=list)
    level: str | None = None
    attributes: dict[str, Sequence[str] | str] = Field(default_factory=dict)

    def to_domain(self) -> AccessContext:
        return AccessContext(
            user_id=self.user_id,
            tenant_id=self.tenant_id,
            workspace_ids=frozenset(self.workspace_ids),
            manager_of=frozenset(self.manager_of),
            labels=frozenset(self.labels),
            ad_groups=frozenset(self.ad_groups),
            level=self.level,
            attributes=self.attributes,
        )


class AccessResourceModel(BaseModel):
    id: str | None = None
    workspace_ids: List[str] = Field(default_factory=list)
    owner_id: str | None = None
    attributes: dict[str, Sequence[str] | str] = Field(default_factory=dict)

    def to_attributes(self) -> dict[str, Sequence[str] | str]:
        payload: dict[str, Sequence[str] | str] = {
            "workspace_ids": self.workspace_ids,
        }
        payload.update(self.attributes)
        if self.id:
            payload["id"] = self.id
        if self.owner_id:
            payload["owner_id"] = self.owner_id
        return payload


class RoleAssignmentRequest(BaseModel):
    user_id: str
    role: str


class ObjectRoleAssignmentRequest(BaseModel):
    user_id: str
    object_id: str
    role: ObjectRole


class AccessEvaluationRequest(BaseModel):
    action: str
    context: AccessContextModel
    resource: AccessResourceModel | None = None
    object_roles: List[ObjectRole] | None = None


class AccessEvaluationResponse(BaseModel):
    decision: AccessDecision
    permissions: List[str]


class AccessAssignmentResponse(BaseModel):
    user_id: str
    roles: List[str]


class RoleCatalogueEntry(BaseModel):
    name: str
    permissions: List[str]
    implied_roles: List[str]


# -- SCIM schemas ----------------------------------------------------------


class SCIMName(BaseModel):
    givenName: str | None = None
    familyName: str | None = None


class SCIMEmail(BaseModel):
    value: str
    primary: bool = True
    type: str | None = "work"


class SCIMUser(BaseModel):
    id: str
    userName: str
    active: bool = True
    displayName: str | None = None
    name: SCIMName | None = None
    emails: List[SCIMEmail] = Field(default_factory=list)
    externalId: str | None = None


class SCIMGroupMember(BaseModel):
    value: str
    display: str | None = None


class SCIMGroup(BaseModel):
    id: str
    displayName: str
    members: List[SCIMGroupMember] = Field(default_factory=list)


class SCIMListResponse(BaseModel):
    Resources: List[dict]
    totalResults: int
    itemsPerPage: int
    startIndex: int = 1
    schemas: List[str] = Field(default_factory=lambda: ["urn:ietf:params:scim:api:messages:2.0:ListResponse"])


class SCIMUserCreateRequest(BaseModel):
    userName: str
    active: bool = True
    displayName: str | None = None
    name: SCIMName | None = None
    emails: List[SCIMEmail] = Field(default_factory=list)
    externalId: str | None = None


class SCIMUserPatchOperation(BaseModel):
    op: str
    path: str | None = None
    value: dict | bool | str | list | None = None


class SCIMPatchRequest(BaseModel):
    schemas: List[str]
    Operations: List[SCIMUserPatchOperation]


class SCIMGroupCreateRequest(BaseModel):
    displayName: str
    members: List[SCIMGroupMember] = Field(default_factory=list)


class SCIMErrorResponse(BaseModel):
    detail: str
    status: int
    schemas: List[str] = Field(default_factory=lambda: ["urn:ietf:params:scim:api:messages:2.0:Error"])
