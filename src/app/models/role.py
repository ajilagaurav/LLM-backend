# app/models/role.py

import uuid
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, JSON, Column, Integer
from pydantic import validator

class Role(SQLModel, table=True):
    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = Field(default=None)
    permissions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("updated_at", always=True)
    def set_updated_at(cls, v, values, **kwargs):
        return datetime.utcnow()


class RoleCreate(SQLModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []


class RoleUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleRead(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    created_at: datetime
    updated_at: datetime