from pydantic import BaseModel
from typing import Optional, List


class TargetUserBase(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    company: str
    job_title: str
    target_id: int


class TargetBase(BaseModel):
    name: str
    target_user: List[TargetUserBase]


class TargetCreate(BaseModel):
    name: str


class TargetResponse(TargetBase):
    id: int
