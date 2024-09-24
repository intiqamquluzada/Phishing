
from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    role: str


class ForgotPassword(BaseModel):
    email: str


class ForgotPasswordConfirm(BaseModel):
    password: str
    password2: str


class User(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

    @classmethod
    def from_orm(cls, obj):
        obj_dict = obj.__dict__.copy()
        obj_dict['role'] = obj.role.value
        return cls(**obj_dict)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(UserBase):
    ...
