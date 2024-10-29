from typing import List
import json

import sqlalchemy
from fastapi import (APIRouter, Depends, HTTPException, status,
                     Form, Request, UploadFile, Body, File)
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta

from phish.utils.files import save_file
from phish.dependencies import get_db
from phish.models.training import Training, TrainingInformation, Question
from phish.models.training import TypeOfTraining as TrainType
from phish.models.users import User as UserModel
from phish.routers.auth import require_role
from phish.schemas.training import (TrainingBase, TrainingInformationBase,
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
        pages_count: int = Form(...),
        preview: UploadFile = File(None),
        presentation: UploadFile = File(None),
        questions: List[str] = Form(...),
        db: Session = Depends(get_db),
        user: UserModel = Depends(require_role(1)),
        request: Request = None
):
    training_info = TrainingInformation(
        question_count=len(questions),
        pages_count=pages_count,
    )

    db.add(training_info)
    db.commit()
    db.refresh(training_info)

    for question in questions:
        create_question = Question(
            question=json.dumps(question),  # Serialize question to JSON
            training_information_id=training_info.id
        )
        db.add(create_question)

    db.commit()

    save_preview_location = save_file(preview, request)
    save_presentation_location = save_file(presentation, request)

    new_training = Training(
        module_name=module_name,
        passing_score=passing_score,
        preview=save_preview_location if preview else None,
        presentation=save_presentation_location if presentation else None,
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
                          pages_count: int = Form(...),
                          preview: UploadFile = File(None),
                          presentation: UploadFile = File(None),
                          questions: List[str] = Form(...),
                          db: Session = Depends(get_db),
                          request: Request = None,
                          user: UserModel = Depends(require_role(TrainType.ADMIN.value))
                          ):
    training = db.query(Training).filter(Training.id == training_id).first()

    if not training:
        raise HTTPException(status_code=404, detail="Training not found")

    save_preview_location = save_file(preview, request)
    save_presentation_location = save_file(presentation, request)

    training_info = db.query(TrainingInformation).filter(
        TrainingInformation.id == training.training_information).first()

    question = db.query(Question).filter(Question.training_information_id == training_info.id)

    if question:
        question.delete(synchronize_session=False) # delete all data
        db.commit()

    training_info.question_count = len(questions)
    training_info.pages_count = pages_count

    for question in questions:
        create_question = Question(
            question=question,
            training_information_id=training_info.id
        )
        db.add(create_question)

    db.commit()

    training.module_name = module_name
    training.passing_score = passing_score
    training.preview = save_preview_location if preview else None
    training.presentation = save_presentation_location if presentation else None

    db.commit()
    db.refresh(training)

    return training


@router.patch("/update/{training_id}", response_model=TrainingResponse, summary="Partially update a training")
def partially_update_training(training_id: int,
                              module_name: str = Form(...),
                              passing_score: int = Form(...),
                              pages_count: int = Form(...),
                              preview: UploadFile = File(None),
                              presentation: UploadFile = File(None),
                              questions: List[str] = Form(...),
                              db: Session = Depends(get_db),
                              request: Request = None,
                              user: UserModel = Depends(require_role(TrainType.ADMIN.value))
                              ):
    training = db.query(Training).filter(Training.id == training_id).first()

    if not training:
        raise HTTPException(status_code=404, detail="Training not found")

    save_preview_location = save_file(preview, request)
    save_presentation_location = save_file(presentation, request)

    training_info = db.query(TrainingInformation).filter(
        TrainingInformation.id == training.training_information).first()

    question = db.query(Question).filter(Question.training_information_id == training_info.id)

    if question:
        question.delete(synchronize_session=False)  # delete all data
        db.commit()

    if questions is not None:
        for question in questions:
            create_question = Question(
                question=question,
                training_information_id=training_info.id
            )
            db.add(create_question)
        db.commit()
    if module_name is not None:
        training.module_name = module_name
    if passing_score is not None:
        training.passing_score = passing_score
    if preview is not None:
        training.preview = save_preview_location if preview else None
    if presentation is not None:
        training.presentation = save_presentation_location if presentation else None

    if questions is not None:
        training_info.question_count = len(questions)
    if pages_count is not None:
        training_info.pages_count = pages_count

    db.commit()
    db.refresh(training)

    return training


@router.delete("/delete/{training_id}", response_model=dict, summary="Delete a training")
def delete_training(training_id: int, db: Session = Depends(get_db),
                    user: UserModel = Depends(require_role(TrainType.ADMIN.value))
                    ):
    training = db.query(Training).filter(Training.id == training_id).first()

    if not training:
        raise HTTPException(status_code=404, detail="Training not found")

    training_info = db.query(TrainingInformation).filter(
        TrainingInformation.id == training.training_information).first()

    db.delete(training)
    db.delete(training_info)
    db.commit()

    return {"detail": "Training deleted successfully"}
