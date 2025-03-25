# app/routers/role_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Security
from typing import List
import uuid
from sqlmodel import Session

from app.models.role import Role, RoleCreate, RoleUpdate, RoleRead
from app.repositories.role_repository import RoleRepository
from app.database import get_db
from app.authentication import verify_token

router = APIRouter()

def get_role_repository(db: Session = Depends(get_db)):
    return RoleRepository(db)

@router.post("/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(
    role: RoleCreate, 
    repo: RoleRepository = Depends(get_role_repository),
    token: str = Security(verify_token)
):
    """
    Create a new role with specified permissions.
    Requires API key authentication.
    """
    return repo.create_role(role)

@router.get("/roles", response_model=List[RoleRead])
def get_all_roles(
    repo: RoleRepository = Depends(get_role_repository),
    token: str = Security(verify_token)
):
    """
    Retrieve all roles.
    Requires API key authentication.
    """
    return repo.get_all_roles()

@router.get("/roles/{role_id}", response_model=RoleRead)
def get_role_by_id(
    role_id: int, 
    repo: RoleRepository = Depends(get_role_repository),
    token: str = Security(verify_token)
):
    """
    Retrieve a specific role by ID.
    Requires API key authentication.
    """
    role = repo.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/roles/{role_id}", response_model=RoleRead)
def update_role(
    role_id: int, 
    role_update: RoleUpdate, 
    repo: RoleRepository = Depends(get_role_repository),
    token: str = Security(verify_token)
):
    """
    Update a role's information.
    Requires API key authentication.
    """
    updated_role = repo.update_role(role_id, role_update)
    if not updated_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return updated_role

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int, 
    repo: RoleRepository = Depends(get_role_repository),
    token: str = Security(verify_token)
):
    """
    Delete a role.
    Requires API key authentication.
    """
    deleted = repo.delete_role(role_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role not found")
    return None