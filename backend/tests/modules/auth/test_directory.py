from app.modules.auth.directory import InMemoryDirectory
from app.modules.auth.schemas import (
    SCIMEmail,
    SCIMGroupCreateRequest,
    SCIMGroupMember,
    SCIMPatchRequest,
    SCIMUserCreateRequest,
)


def test_directory_user_lifecycle_roundtrip():
    directory = InMemoryDirectory()

    create_request = SCIMUserCreateRequest(
        userName="jane.doe",
        displayName="Jane Doe",
        emails=[SCIMEmail(value="jane@example.com")],
        externalId="ext-123",
    )

    user = directory.create_user(create_request)
    assert user.userName == "jane.doe"
    assert user.emails[0].value == "jane@example.com"

    fetched = directory.get_user(user.id)
    assert fetched is not None
    assert fetched.displayName == "Jane Doe"

    patch_request = SCIMPatchRequest(
        schemas=["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        Operations=[
            {
                "op": "Replace",
                "path": "displayName",
                "value": "Jane Smith",
            }
        ],
    )

    updated = directory.patch_user(user.id, [op.model_dump(exclude_none=True) for op in patch_request.Operations])
    assert updated is not None
    assert updated.displayName == "Jane Smith"

    replaced = directory.replace_user(
        user.id,
        SCIMUserCreateRequest(
            userName="jane.roe",
            displayName="Jane Roe",
            emails=[SCIMEmail(value="jane.roe@example.com")],
            active=False,
        ),
    )
    assert replaced is not None
    assert replaced.userName == "jane.roe"
    assert replaced.active is False

    assert directory.delete_user(user.id) is True
    assert directory.get_user(user.id) is None


def test_directory_group_membership_management():
    directory = InMemoryDirectory()

    group = directory.create_group(
        SCIMGroupCreateRequest(displayName="Product", members=[])
    )

    member = SCIMGroupMember(value="user-1", display="User One")
    updated = directory.add_member_to_group(group.id, member)
    assert updated is not None
    assert any(m.value == "user-1" for m in updated.members)

    cleaned = directory.remove_member_from_group(group.id, "user-1")
    assert cleaned is not None
    assert all(m.value != "user-1" for m in cleaned.members)

    assert directory.delete_group(group.id) is True
