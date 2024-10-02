from pydantic import BaseModel
from enum import Enum as PyEnum
from phish.schemas.users import User, UserCreate, UserPatch
from typing import Optional


class Status(PyEnum):
    ACTIVE = "ACTIVE"
    INVITED = "INVITED"


class AdministrationBase(BaseModel):
    name: str
    status: Status
    is_active: bool
    user_id: int
    campaign_id: int
    user: User

    class Config:
        orm_mode = True


class AdministrationUpdate(BaseModel):
    name: str
    is_active: bool
    user: UserPatch

    class Config:
        orm_mode = True


class AdministrationPatch(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    user: UserCreate

    class Config:
        orm_mode = True


class AdministrationResponse(AdministrationBase):
    id: int

    class Config:
        orm_mode = True


class SendInvite(BaseModel):
    email: str
