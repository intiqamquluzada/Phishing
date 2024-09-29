from pydantic import BaseModel
from typing import Optional
from enum import Enum as PyEnum


class EmailDifficulty(PyEnum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class EmailTemplateBase(BaseModel):
    name: str
    description: str
    difficulty: EmailDifficulty
    subject: str
    body: str

    class Config:
        orm_mode = True


class EmailTemplateResponse(EmailTemplateBase):
    id: int
    file_path: Optional[str]

    class Config:
        orm_mode = True
