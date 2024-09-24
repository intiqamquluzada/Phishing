from typing import List

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta

from phish.dependencies import get_db
from phish.models.training import Training, TrainingInformation
from phish.models.training import TypeOfTraining
from phish.models.users import User as UserModel
from phish.routers.auth import require_role
from phish.schemas.training import (TrainingBase, TrainingInformationBase,
                                    TrainingResponse, TrainingCreate, TrainingPatch)

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
def create_new_training(
        training: TrainingCreate,
        db: Session = Depends(get_db),
        user: UserModel = Depends(require_role(TypeOfTraining.ADMIN))
):
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
def update_training_by_id(training_id: int, updated_training: TrainingCreate, db: Session = Depends(get_db),
                          user: UserModel = Depends(require_role(TypeOfTraining.ADMIN))):
    training = db.query(Training).filter(Training.id == training_id).first()

    if training:
        training_info = db.query(TrainingInformation).filter(
            TrainingInformation.id == training.training_information).first()

        training_info.question_count = updated_training.info.question_count
        training_info.pages_count = updated_training.info.pages_count
        training_info.type = updated_training.info.type.value  # Convert enum to string

        training.module_name = updated_training.module_name
        training.passing_score = updated_training.passing_score
        training.preview = updated_training.preview
        training.compliance = updated_training.compliance

        db.commit()
        db.refresh(training)

    return training


@router.patch("/update/{training_id}", response_model=TrainingResponse, summary="Partially update a training")
def partially_update_training(training_id: int, updated_fields: TrainingPatch, db: Session = Depends(get_db),
                              user: UserModel = Depends(require_role(TypeOfTraining.ADMIN))):
    training = db.query(Training).filter(Training.id == training_id).first()

    if not training:
        raise HTTPException(status_code=404, detail="Training not found")

    training_info = db.query(TrainingInformation).filter(
        TrainingInformation.id == training.training_information).first()

    if updated_fields.module_name is not None:
        training.module_name = updated_fields.module_name
    if updated_fields.passing_score is not None:
        training.passing_score = updated_fields.passing_score
    if updated_fields.preview is not None:
        training.preview = updated_fields.preview
    if updated_fields.compliance is not None:
        training.compliance = updated_fields.compliance

    if updated_fields.info:
        if updated_fields.info.question_count is not None:
            training_info.question_count = updated_fields.info.question_count
        if updated_fields.info.pages_count is not None:
            training_info.pages_count = updated_fields.info.pages_count
        if updated_fields.info.type is not None:
            training_info.type = updated_fields.info.type.value

    db.commit()
    db.refresh(training)

    return training


@router.delete("/delete/{training_id}", response_model=dict, summary="Delete a training")
def delete_training(training_id: int, db: Session = Depends(get_db),
                    user: UserModel = Depends(require_role(TypeOfTraining.ADMIN))):
    training = db.query(Training).filter(Training.id == training_id).first()

    if not training:
        raise HTTPException(status_code=404, detail="Training not found")

    training_info = db.query(TrainingInformation).filter(
        TrainingInformation.id == training.training_information).first()

    db.delete(training)
    db.delete(training_info)
    db.commit()

    return {"detail": "Training deleted successfully"}
