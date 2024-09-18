from pydantic import BaseModel
from typing import Optional, List

class TrainingInformationBase(BaseModel):
    question_count: int
    pages_count: int
    type: str

    class Config:
        orm_mode = True


class TrainingBase(BaseModel):
    id: int
    module_name: str
    passing_score: int
    preview: str
    compliance: bool
    info: TrainingInformationBase

    class Config:
        orm_mode = True
