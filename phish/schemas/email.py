from pydantic import BaseModel
from typing import Optional
from enum import Enum as PyEnum


class EmailType(PyEnum):
    STANDARD = "STANDARD"
    CONVERSATIONAL = "CONVERSATIONAL"


class EmailDifficulty(PyEnum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class EmailTemplateBase(BaseModel):
    name: str
    description: str
    difficulty: EmailDifficulty
    type: EmailType
    payload_type: str
    subject: str
    body: str

    class Config:
        orm_mode = True


class EmailTemplateResponse(EmailTemplateBase):
    id: int

    class Config:
        orm_mode = True


class EmailTemplatePatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[EmailDifficulty] = None
    type: Optional[EmailType] = None
    payload_type: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None

    class Config:
        orm_mode = True
