
from pydantic import BaseModel
from typing import Optional
from phish.schemas.role import RoleResponse

class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    role_id: int


class UserPatch(UserBase):
    password: Optional[str]
    role_id: Optional[int]


class ForgotPassword(BaseModel):
    email: str


class ForgotPasswordConfirm(BaseModel):
    password: str
    password2: str


class User(UserBase):
    id: int
    role: RoleResponse

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


# from phish.schemas.role import RoleResponse
#
# User.update_forward_refs()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(UserBase):
    ...
