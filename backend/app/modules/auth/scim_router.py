"""SCIM 2.0 provisioning endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from .directory import directory
from .schemas import (
    SCIMErrorResponse,
    SCIMGroup,
    SCIMGroupCreateRequest,
    SCIMGroupMember,
    SCIMListResponse,
    SCIMPatchRequest,
    SCIMUser,
    SCIMUserCreateRequest,
)

scim_router = APIRouter(prefix="/scim/v2", tags=["scim"])


@scim_router.get("/Users", response_model=SCIMListResponse)
def list_users() -> SCIMListResponse:
    users = [user.dict() for user in directory.list_users()]
    return SCIMListResponse(Resources=users, totalResults=len(users), itemsPerPage=len(users))


@scim_router.post(
    "/Users",
    response_model=SCIMUser,
    status_code=status.HTTP_201_CREATED,
)
def create_user(payload: SCIMUserCreateRequest) -> SCIMUser:
    return directory.create_user(payload)


@scim_router.get("/Users/{user_id}", response_model=SCIMUser)
def get_user(user_id: str) -> SCIMUser:
    user = directory.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@scim_router.put("/Users/{user_id}", response_model=SCIMUser)
def replace_user(user_id: str, payload: SCIMUserCreateRequest) -> SCIMUser:
    user = directory.replace_user(user_id, payload)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@scim_router.patch("/Users/{user_id}", response_model=SCIMUser)
def patch_user(user_id: str, payload: SCIMPatchRequest) -> SCIMUser:
    user = directory.patch_user(user_id, [op.dict(exclude_none=True) for op in payload.Operations])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@scim_router.delete("/Users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str) -> None:
    if not directory.delete_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@scim_router.get("/Groups", response_model=SCIMListResponse)
def list_groups() -> SCIMListResponse:
    groups = [group.dict() for group in directory.list_groups()]
    return SCIMListResponse(Resources=groups, totalResults=len(groups), itemsPerPage=len(groups))


@scim_router.post("/Groups", response_model=SCIMGroup, status_code=status.HTTP_201_CREATED)
def create_group(payload: SCIMGroupCreateRequest) -> SCIMGroup:
    return directory.create_group(payload)


@scim_router.get("/Groups/{group_id}", response_model=SCIMGroup)
def get_group(group_id: str) -> SCIMGroup:
    group = directory.get_group(group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group


@scim_router.put("/Groups/{group_id}", response_model=SCIMGroup)
def replace_group(group_id: str, payload: SCIMGroupCreateRequest) -> SCIMGroup:
    group = directory.replace_group(group_id, payload)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group


@scim_router.delete("/Groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_id: str) -> None:
    if not directory.delete_group(group_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")


@scim_router.post("/Groups/{group_id}/members", response_model=SCIMGroup)
def add_group_member(group_id: str, member: SCIMGroupMember) -> SCIMGroup:
    group = directory.add_member_to_group(group_id, member)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group


@scim_router.delete("/Groups/{group_id}/members/{member_id}", response_model=SCIMGroup)
def remove_group_member(group_id: str, member_id: str) -> SCIMGroup:
    group = directory.remove_member_from_group(group_id, member_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group


@scim_router.exception_handler(Exception)
async def scim_exception_handler(_: Exception) -> JSONResponse:
    """Return RFC compliant error structures for unexpected issues."""

    error = SCIMErrorResponse(detail="Internal Server Error", status=500)
    return JSONResponse(status_code=500, content=error.dict())
