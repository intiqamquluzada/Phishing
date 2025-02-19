from pydantic import BaseModel
from typing import Optional, List


class TargetUserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    company: str
    job_title: str
    target_id: int


class TargetUserPatch(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    target_id: Optional[int] = None


class TargetUserResponse(TargetUserBase):
    id: int


class TargetBase(BaseModel):
    name: str
    target_users: List[TargetUserResponse]


class TargetUpdate(BaseModel):
    name: str

class TargetUpdatePatch(BaseModel):
    name: Optional[str] = None


class TargetResponse(TargetBase):
    id: int
