# app/repositories/role_repository.py

from typing import List, Optional
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, Session
from fastapi import HTTPException
from app.models.role import Role, RoleCreate, RoleUpdate

class RoleRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_role(self, role_data: RoleCreate) -> Role:
        try:
            role = Role(
                name=role_data.name,
                description=role_data.description,
                permissions=role_data.permissions
            )
            self.session.add(role)
            self.session.commit()
            self.session.refresh(role)
            return role
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(status_code=400, detail="Role with this name already exists")
        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create role: {str(e)}")

    def get_all_roles(self) -> List[Role]:
        statement = select(Role).order_by(Role.name)
        results = self.session.execute(statement).scalars().all()
        return results

    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        statement = select(Role).where(Role.id == role_id)
        role = self.session.execute(statement).scalar_one_or_none()
        return role


    def update_role(self, role_id: int, role_update: RoleUpdate) -> Optional[Role]:
        role = self.get_role_by_id(role_id)
        if not role:
            return None
            
        update_data = role_update.dict(exclude_unset=True)
        
        if update_data:
            # Update the fields
            for key, value in update_data.items():
                setattr(role, key, value)
                
            # Always update the updated_at timestamp
            role.updated_at = datetime.utcnow()
            
            try:
                self.session.add(role)
                self.session.commit()
                self.session.refresh(role)
            except IntegrityError:
                self.session.rollback()
                raise HTTPException(status_code=400, detail="Role with this name already exists")
            except Exception as e:
                self.session.rollback()
                raise HTTPException(status_code=500, detail=f"Failed to update role: {str(e)}")
                
        return role

    def delete_role(self, role_id: int) -> bool:
        role = self.get_role_by_id(role_id)
        if not role:
            return False
            
        try:
            self.session.delete(role)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete role: {str(e)}")