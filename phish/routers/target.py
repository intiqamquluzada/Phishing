from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from phish.dependencies import get_db
from phish.models.target import Target, TargetUser
from phish.schemas.target import TargetBase, TargetCreate, TargetResponse
from typing import List
import pandas as pd
from io import BytesIO


router = APIRouter(
    prefix="/target",
    tags=["Target"]
)

@router.get("/",
            response_model=List[TargetResponse],
            summary="List of Target",
            description="List of Target")
async def target_list(db: Session = Depends(get_db)):
    targets = db.query(Target).all()

    if not targets:
        return HTTPException(status_code=404, detail="Target not found")

    return targets


@router.get("/detail/{target_id}",
            response_model=TargetResponse,
            summary="Detail of Target",
            description="Detail of Target")
async def target_detail(target_id: int,
                        db: Session = Depends(get_db)):
    target = db.query(Target).filter(Target.id == target_id).first()

    if not target:
        return HTTPException(status_code=404, detail="Target not found")

    return target


@router.post("/create",
             response_model=TargetResponse,
             summary="Create a New Target List")
async def create_target(list_name: str = Form(...),
                        file: UploadFile = File(...),
                        db: Session = Depends(get_db)):

    new_target = Target(
        name=list_name
    )

    db.add(new_target)
    db.commit()

    contents = await file.read()
    # Convert the bytes data into a BytesIO object
    datas = pd.read_excel(BytesIO(contents), engine='openpyxl')

    # iterate the dataframe
    for index, row in datas.iterrows():
        new_target_user = TargetUser(
            first_name=row.iloc[0],
            last_name=row.iloc[1],
            email=row.iloc[2],
            company=row.iloc[3],
            job_title=row.iloc[4],
            target_id=new_target.id,
        )

        db.add(new_target_user)

    db.commit()
    db.refresh(new_target)

    return new_target
