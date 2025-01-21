from fastapi import APIRouter, HTTPException, Query

from shared.models import Organization
from src.dependencies import ExistingOrganization

router = APIRouter(tags=["organizations"])


# Disabled because only admins should be able to access this, and we don't have
# roles implemented yet.
# @router.post(
#     "/",
#     response_model=Organization,
#     status_code=status.HTTP_201_CREATED,
#     operation_id="create_organization",
# )
# async def create_organization(body: OrganizationCreate):
#     """
#     Create a new organization.

#     - Fails with 409 if 'name' or 'secret_code' is already in use
#     """
#     new_org = Organization(
#         name=body.name.strip(),
#         secret_code=SecretStr(body.secret_code.strip()),
#     )

#     try:
#         return await new_org.insert()
#     except DuplicateKeyError:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Organization name or secret_code already in use.",
#         )


# Disabled because only admins should be able to access this, and we don't have
# roles implemented yet.
# @router.get(
#     "/",
#     response_model=list[Organization],
#     operation_id="list_organizations",
# )
# async def list_organizations():
#     """
#     List all organizations.
#     (Admins only in real scenario, but minimal for now)
#     """
#     return (
#         await Organization.find_all()
#         .sort(
#             -Organization.created_at,  # type: ignore
#         )
#         .to_list()
#     )


@router.get(
    "/by-secret-code",
    response_model=Organization,
    operation_id="get_organization_by_secret_code",
)
async def get_organization_by_secret_code(
    code: str = Query(..., description="Organization secret code"),
):
    """
    Retrieve an organization by its secret code.
    Returns 404 if none found.
    """
    org = await Organization.find_one(Organization.secret_code == code)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.get(
    "/{organization_id}",
    response_model=Organization,
    operation_id="get_organization",
)
async def get_organization(organization: ExistingOrganization):
    """
    Retrieve a single organization by ID.
    """
    return organization
