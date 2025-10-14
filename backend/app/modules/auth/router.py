"""API router for the Auth domain."""
from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from ...core.config import Settings, get_settings
from ...schemas.health import HealthStatus
from ...services.access_policies import ObjectRole, policy_engine
from .schemas import (
    AccessAssignmentResponse,
    AccessEvaluationRequest,
    AccessEvaluationResponse,
    AccessContextModel,
    AccessResourceModel,
    AzureLogoutResponse,
    AzureOAuthAuthorizeRequest,
    AzureOAuthAuthorizeResponse,
    AzureOAuthRefreshRequest,
    AzureOAuthTokenRequest,
    AzureOAuthTokenResponse,
    ObjectRoleAssignmentRequest,
    RoleAssignmentRequest,
    RoleCatalogueEntry,
)
from .scim_router import scim_router
from .services.azure import AzureOAuthClient

logger = logging.getLogger(__name__)

router = APIRouter()
router.include_router(scim_router)


def _get_policy_engine():
    return policy_engine


@router.get("/health", response_model=HealthStatus, status_code=status.HTTP_200_OK)
def healthcheck() -> HealthStatus:
    """Return a simple status payload for liveness probes."""

    return HealthStatus(status="ok", module="auth")


@router.post("/oauth2/authorize", response_model=AzureOAuthAuthorizeResponse)
async def oauth_authorize(
    payload: AzureOAuthAuthorizeRequest,
    settings: Settings = Depends(get_settings),
) -> AzureOAuthAuthorizeResponse:
    """Return the Azure AD authorize URL for PKCE-based flows."""

    client = AzureOAuthClient(settings)
    url, verifier = client.build_authorization_url(
        state=payload.state,
        nonce=payload.nonce,
        scopes=payload.scopes,
        redirect_uri=payload.redirect_uri,
        code_verifier=None,
        code_challenge=payload.code_challenge,
        code_challenge_method=payload.code_challenge_method or "S256",
    )
    return AzureOAuthAuthorizeResponse(authorization_url=url, code_verifier=verifier)


@router.post("/oauth2/token", response_model=AzureOAuthTokenResponse)
async def oauth_token(
    payload: AzureOAuthTokenRequest,
    settings: Settings = Depends(get_settings),
) -> AzureOAuthTokenResponse:
    """Exchange an authorization code for tokens."""

    client = AzureOAuthClient(settings)
    try:
        return await client.exchange_code_for_token(
            code=payload.code,
            redirect_uri=payload.redirect_uri,
            code_verifier=payload.code_verifier,
        )
    except httpx.HTTPStatusError as exc:  # pragma: no cover - passthrough to client
        logger.exception("Failed to exchange code with Azure AD")
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Failed to exchange authorization code",
        ) from exc


@router.post("/oauth2/refresh", response_model=AzureOAuthTokenResponse)
async def oauth_refresh(
    payload: AzureOAuthRefreshRequest,
    settings: Settings = Depends(get_settings),
) -> AzureOAuthTokenResponse:
    """Refresh an access token using a refresh token."""

    client = AzureOAuthClient(settings)
    try:
        return await client.refresh_access_token(refresh_token=payload.refresh_token)
    except httpx.HTTPStatusError as exc:  # pragma: no cover - passthrough to client
        logger.exception("Failed to refresh Azure AD token")
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Failed to refresh token",
        ) from exc


@router.post("/oauth2/logout", response_model=AzureLogoutResponse)
async def oauth_logout(
    settings: Settings = Depends(get_settings),
) -> AzureLogoutResponse:
    """Provide the logout URL for front-channel sign-out."""

    client = AzureOAuthClient(settings)
    return AzureLogoutResponse(logout_url=client.build_logout_url())


@router.post("/roles/assign", response_model=AccessAssignmentResponse)
def assign_role(
    payload: RoleAssignmentRequest,
    engine=Depends(_get_policy_engine),
) -> AccessAssignmentResponse:
    """Assign a platform role to a user."""

    try:
        engine.assign_role(payload.user_id, payload.role)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    roles = sorted(engine.get_assignments(payload.user_id))
    return AccessAssignmentResponse(user_id=payload.user_id, roles=roles)


@router.post("/roles/revoke", response_model=AccessAssignmentResponse)
def revoke_role(
    payload: RoleAssignmentRequest,
    engine=Depends(_get_policy_engine),
) -> AccessAssignmentResponse:
    """Revoke a role from a user."""

    engine.revoke_role(payload.user_id, payload.role)
    roles = sorted(engine.get_assignments(payload.user_id))
    return AccessAssignmentResponse(user_id=payload.user_id, roles=roles)


@router.post("/roles/object", response_model=AccessAssignmentResponse)
def assign_object_role(
    payload: ObjectRoleAssignmentRequest,
    engine=Depends(_get_policy_engine),
) -> AccessAssignmentResponse:
    """Assign an object-level role to a user."""

    engine.grant_object_role(payload.user_id, payload.object_id, payload.role)
    roles = sorted(engine.get_assignments(payload.user_id))
    return AccessAssignmentResponse(user_id=payload.user_id, roles=roles)


@router.post("/roles/evaluate", response_model=AccessEvaluationResponse)
def evaluate_access(
    payload: AccessEvaluationRequest,
    engine=Depends(_get_policy_engine),
) -> AccessEvaluationResponse:
    """Evaluate whether the supplied action is permitted."""

    context = payload.context.to_domain()
    resource_attributes = payload.resource.to_attributes() if payload.resource else {}
    decision, permissions = engine.is_action_allowed(
        user_id=context.user_id,
        action=payload.action,
        context=context,
        resource_attributes=resource_attributes,
        object_roles=payload.object_roles,
    )
    return AccessEvaluationResponse(decision=decision, permissions=sorted(permissions))


@router.get("/roles/catalogue", response_model=list[RoleCatalogueEntry])
def list_roles(engine=Depends(_get_policy_engine)) -> list[RoleCatalogueEntry]:
    """Return the registered role catalogue."""

    entries = []
    for role in engine.describe_roles():
        entries.append(
            RoleCatalogueEntry(
                name=role.name,
                permissions=sorted(role.permissions),
                implied_roles=sorted(role.implied_roles),
            )
        )
    return entries


@router.get("/roles/decision-examples", response_model=list[AccessEvaluationResponse])
def decision_examples(engine=Depends(_get_policy_engine)) -> list[AccessEvaluationResponse]:
    """Return canned examples showing RBAC + ABAC + object-role interplay."""

    example_payload = AccessEvaluationRequest(
        action="workflow:approve",
        context=AccessContextModel(
            user_id="user-1",
            tenant_id="tenant-1",
            workspace_ids=["workspace-1"],
            manager_of=["user-2"],
            labels=["okr-expert"],
        ),
        resource=AccessResourceModel(
            id="objective-1",
            workspace_ids=["workspace-1"],
            owner_id="user-2",
        ),
        object_roles=[ObjectRole.APPROVER],
    )
    result = evaluate_access(example_payload, engine)
    return [result]
