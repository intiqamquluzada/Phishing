from pydantic import BaseModel
from enum import Enum as PyEnum
from phish.schemas.users import User

class Status(PyEnum):
    ACTIVE = "ACTIVE"
    INVITED = "INVITED"


class AdministrationBase(BaseModel):
    name: str
    status: Status
    is_active: bool
    user_id: int
    campaign_id: int


class AdministrationResponse(AdministrationBase):
    id: int


class SendInvite(BaseModel):
    email: str
