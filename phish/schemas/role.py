from pydantic import BaseModel, validator
from enum import Enum as PyEnum
from phish.models.role import Role
from datetime import datetime
from typing import Optional, Union, List
from phish.schemas.users import User


class Permission(PyEnum):
    TESTPER1 = "TESTPER1"
    TESTPER2 = "TESTPER2"
    TESTPER3 = "TESTPER3"


class RoleBase(BaseModel):
    name: str
    description: str
    permission: List[Permission]
    user_id: int

    class Config:
        orm_mode = True


class RolePatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission: Optional[List[Permission]] = None
    user_id: Optional[int] = None

    class Config:
        orm_mode = True

    @validator('permission', pre=True, always=True)
    def convert_empty_string_to_none(cls, v):
        if v == "":
            return None
        return v


class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    user: User

    class Config:
        orm_mode = True

    @validator('permission', pre=True, always=True)
    def parse_permissions(cls, v):
        if isinstance(v, str) and v == "":
            return []  # Return an empty list instead of an empty string
        return [Permission(p) for p in v.split(',')] if isinstance(v, str) else v