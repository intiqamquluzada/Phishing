from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True  # allows arbitrary types


class Token(BaseModel):
        access_token: str
        token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
