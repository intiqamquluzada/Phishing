from typing import List

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta

from phish.dependencies import get_db
from phish.models.training import Training, TrainingInformation

from phish.models.users import User as UserModel
from phish.schemas.training import (TrainingBase, TrainingInformationBase,
                                    TrainingResponse, TrainingCreate)


router = APIRouter(
    prefix="/trainings",
    tags=["Training"]
)


@router.get("/", response_model=List[TrainingBase],
            summary="List of trainings", description="List of trainings")
async def get_trainings(db: Session = Depends(get_db)):
    trainings = db.query(Training).all()

    if not trainings:
        raise HTTPException(status_code=404, detail="No trainings found")

    return trainings


@router.get("/detail/{training_id}/",
            response_model=TrainingResponse,
            summary="Detail of training",
            description="Detail of training")
async def training_detail(training_id: int, db: Session = Depends(get_db)):
    return db.query(Training).filter(Training.id == training_id).first()


@router.post("/create/", response_model=TrainingResponse, summary="Create a new training")
def create_new_training(training: TrainingCreate, db: Session = Depends(get_db)):
    print("AEEEEE")
    training_info = TrainingInformation(
        question_count=training.info.question_count,
        pages_count=training.info.pages_count,
        type=training.info.type.value
    )

    db.add(training_info)
    db.commit()
    db.refresh(training_info)

    new_training = Training(
        module_name=training.module_name,
        passing_score=training.passing_score,
        preview=training.preview,
        compliance=training.compliance,
        training_information=training_info.id
    )

    db.add(new_training)
    db.commit()
    db.refresh(new_training)

    return new_training


@router.put("/update/{training_id}", response_model=TrainingResponse, summary="Update training")
def update_training_by_id(training_id: int, updated_training: TrainingCreate, db: Session = Depends(get_db)):
    training = db.query(Training).filter(Training.id == training_id).first()

    if training:
        training_info = db.query(TrainingInformation).filter(
            TrainingInformation.id == training.training_information).first()
        training_info.question_count = updated_training.info.question_count
        training_info.pages_count = updated_training.info.pages_count
        training_info.type = updated_training.info.type

        training.module_name = updated_training.module_name
        training.passing_score = updated_training.passing_score
        training.preview = updated_training.preview
        training.compliance = updated_training.compliance

        db.commit()
        db.refresh(training)

    return training


@router.put("/update/{training_id}", response_model=TrainingResponse, summary="Update training")
def update_training_by_id(training_id: int, updated_training: TrainingCreate, db: Session = Depends(get_db)):
    training = db.query(Training).filter(Training.id == training_id).first()

    if training:
        training_info = db.query(TrainingInformation).filter(
            TrainingInformation.id == training.training_information).first()
        training_info.question_count = updated_training.info.question_count
        training_info.pages_count = updated_training.info.pages_count
        training_info.type = updated_training.info.type

        training.module_name = updated_training.module_name
        training.passing_score = updated_training.passing_score
        training.preview = updated_training.preview
        training.compliance = updated_training.compliance

        db.commit()
        db.refresh(training)



