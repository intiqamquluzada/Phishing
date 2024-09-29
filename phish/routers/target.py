from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from phish.dependencies import get_db
from phish.models.target import Target
from phish.schemas.target import TargetBase, TargetCreate, TargetResponse


router = APIRouter(
    prefix="/target",
    tags=["Target"]
)

@router.post("/create",
             #response_model=TargetResponse,
             summary="Create a New Target List")
async def create_target(list_name: str = Form(...),
                        file: UploadFile = File(...),
                        db: Session = Depends(get_db)):

    print(list_name)
    print(file.filename)

    return {"success": "resp"}
