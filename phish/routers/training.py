from typing import List

import sqlalchemy
from fastapi import (APIRouter, Depends, HTTPException, status,
                     Form, Request, UploadFile, File)
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta

from phish.utils.files import save_file
from phish.dependencies import get_db
from phish.models.training import Training, TrainingInformation
from phish.models.training import TypeOfTraining as TrainType
from phish.models.users import User as UserModel
from phish.routers.auth import require_role
from phish.schemas.training import (TypeOfTraining, TrainingBase, TrainingInformationBase,
                                    TrainingResponse, TrainingCreate, TrainingPatch)


router = APIRouter(
    prefix="/trainings",
    tags=["Training"]
)


@router.get("/", response_model=List[TrainingResponse],
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
        module_name: str = Form(...),
        passing_score: int = Form(...),
        compliance: bool = Form(...),
        question_count: int = Form(...),
        pages_count: int = Form(...),
        type: TypeOfTraining = Form(...),
        db: Session = Depends(get_db),
        preview: UploadFile = File(None),
        # user: UserModel = Depends(require_role(TrainType.ADMIN))
):
    training_info = TrainingInformation(
        question_count=question_count,
        pages_count=pages_count,
        type=type.value
    )

    db.add(training_info)
    db.commit()
    db.refresh(training_info)

    save_location = save_file(preview, "training_preview")

    new_training = Training(
        module_name=module_name,
        passing_score=passing_score,
        preview=save_location if preview else None,
        compliance=compliance,
        training_information=training_info.id
    )

    db.add(new_training)
    db.commit()
    db.refresh(new_training)

    return new_training


@router.put("/update/{training_id}", response_model=TrainingResponse, summary="Update training")
def update_training_by_id(training_id: int,
                          module_name: str = Form(...),
                          passing_score: int = Form(...),
                          compliance: bool = Form(...),
                          question_count: int = Form(...),
                          pages_count: int = Form(...),
                          type: TypeOfTraining = Form(...),
                          preview: UploadFile = File(None),
                          db: Session = Depends(get_db),
                          # user: UserModel = Depends(require_role(TrainType.ADMIN))
                          ):
    training = db.query(Training).filter(Training.id == training_id).first()

    if not training:
        raise HTTPException(status_code=404, detail="Training not found")

    save_location = save_file(preview, "training_preview")

    training_info = db.query(TrainingInformation).filter(
        TrainingInformation.id == training.training_information).first()

    training_info.question_count = question_count
    training_info.pages_count = pages_count
    training_info.type = type.value  # Convert enum to string

    training.module_name = module_name
    training.passing_score = passing_score
    training.compliance = compliance
    training.preview = save_location if preview else None

    db.commit()
    db.refresh(training)

    return training


@router.patch("/update/{training_id}", response_model=TrainingResponse, summary="Partially update a training")
def partially_update_training(training_id: int,
                              module_name: str = Form(...),
                              passing_score: int = Form(...),
                              compliance: bool = Form(...),
                              question_count: int = Form(...),
                              pages_count: int = Form(...),
                              type: TypeOfTraining = Form(...),
                              preview: UploadFile = File(None),
                              db: Session = Depends(get_db),
                              # user: UserModel = Depends(require_role(TrainType.ADMIN))
                              ):
    training = db.query(Training).filter(Training.id == training_id).first()

    if not training:
        raise HTTPException(status_code=404, detail="Training not found")

    save_location = save_file(preview, "training_preview")

    training_info = db.query(TrainingInformation).filter(
        TrainingInformation.id == training.training_information).first()

    if module_name is not None:
        training.module_name = module_name
    if passing_score is not None:
        training.passing_score = passing_score
    if preview is not None:
        training.preview = save_location if preview else None
    if compliance is not None:
        training.compliance = compliance

    if question_count is not None:
        training_info.question_count = question_count
    if pages_count is not None:
        training_info.pages_count = pages_count
    if type is not None:
        training_info.type = type.value

    db.commit()
    db.refresh(training)

    return training


@router.delete("/delete/{training_id}", response_model=dict, summary="Delete a training")
def delete_training(training_id: int, db: Session = Depends(get_db),
                    user: UserModel = Depends(require_role(TrainType.ADMIN))):
    training = db.query(Training).filter(Training.id == training_id).first()

    if not training:
        raise HTTPException(status_code=404, detail="Training not found")

    training_info = db.query(TrainingInformation).filter(
        TrainingInformation.id == training.training_information).first()

    db.delete(training)
    db.delete(training_info)
    db.commit()

    return {"detail": "Training deleted successfully"}
