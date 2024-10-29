from pydantic import BaseModel
from typing import Optional
from typing import Optional, List
from pydantic import validator
import json



class QuestionBase(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    id: int
    question: str

    @validator("question", pre=True)
    def parse_question(cls, value):
        return value.strip()



class TrainingInformationBase(BaseModel):
    question_count: int
    pages_count: int
    question: List[QuestionResponse]

    class Config:
        orm_mode = True


class TrainingBase(BaseModel):
    module_name: str
    passing_score: int


class TrainingCreate(TrainingBase):
    info: TrainingInformationBase


class TrainingResponse(TrainingBase):
    id: int
    preview: Optional[str] = None
    presentation: Optional[str] = None
    info: TrainingInformationBase

    class Config:
        orm_mode = True


class TrainingPatch(TrainingBase):
    info: Optional[TrainingInformationBase] = None
