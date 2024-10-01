from pydantic import BaseModel
from typing import Optional
from enum import Enum as PyEnum


class TypeOfTraining(PyEnum):
    SIMPLE = "SIMPLE"
    PREMIUM = "PREMIUM"


class TrainingInformationBase(BaseModel):
    question_count: int
    pages_count: int
    type: TypeOfTraining

    class Config:
        orm_mode = True


class TrainingBase(BaseModel):
    module_name: str
    passing_score: int
    compliance: bool


class TrainingCreate(TrainingBase):
    info: TrainingInformationBase


class TrainingResponse(TrainingBase):
    id: int
    preview: Optional[str] = None
    info: TrainingInformationBase

    class Config:
        orm_mode = True


class TrainingPatch(TrainingBase):
    info: Optional[TrainingInformationBase] = None

