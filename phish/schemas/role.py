from pydantic import BaseModel, validator
from enum import Enum as PyEnum
from datetime import datetime
from typing import Optional, List

class Permission(PyEnum):
    TESTPER1 = "TESTPER1"
    TESTPER2 = "TESTPER2"
    TESTPER3 = "TESTPER3"

class RoleBase(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

class RoleCreateBase(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

class RoleResponse(RoleBase):
    created_at: datetime
    permissions: List[Permission]

    class Config:
        orm_mode = True
        from_attributes = True

    @validator('permissions', pre=True, always=True)
    def parse_permissions(cls, v):
        if isinstance(v, str) and v == "":
            return []  # Return an empty list instead of an empty string
        return [Permission(p) for p in v.split(',')] if isinstance(v, str) else v

class RolePatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[Permission]] = None  # Adjusted field name to match RoleResponse

    class Config:
        orm_mode = True
        from_attributes = True  # Enable from_orm

    @validator('permissions', pre=True, always=True)
    def convert_empty_string_to_none(cls, v):
        if v == "":
            return None
        return v


class RoleListResponse(BaseModel):
    roles: List[RoleResponse]
    total_roles: int