from typing import List
from fastapi import (APIRouter, Depends, HTTPException, status,
                     Form, Request, UploadFile, File)
from sqlalchemy.orm import Session

from phish.utils.files import save_file
from phish.dependencies import get_db
from phish.models.training import Training, TrainingInformation, Question
from phish.models.training import TypeOfTraining as TrainType
from phish.models.users import User as UserModel
from phish.routers.auth import require_role
from phish.schemas.training import (TrainingBase, TrainingInformationBase,
                                    TrainingResponse, TrainingCreate, TrainingPatch, QuestionResponse)

router = APIRouter(
    prefix="/trainings",
    tags=["Training"]
)


@router.get("/questions/", response_model=List[QuestionResponse],
            summary="List all questions", description="Fetches all available questions")
async def get_questions(db: Session = Depends(get_db)):
    questions = db.query(Question).all()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found")

    return [QuestionResponse(id=question.id, question=question.question) for question in questions]


@router.get("/", response_model=List[TrainingResponse],
            summary="List of trainings", description="Fetches a list of trainings")
async def get_trainings(db: Session = Depends(get_db)):
    trainings = db.query(Training).all()
    if not trainings:
        raise HTTPException(status_code=404, detail="No trainings found")

    training_responses = []
    for training in trainings:
        training_info = db.query(TrainingInformation).filter(
            TrainingInformation.id == training.training_information).first()
        questions = db.query(Question).filter(
            Question.training_information_id == training_info.id).all()

        training_response = TrainingResponse(
            id=training.id,
            module_name=training.module_name,
            passing_score=training.passing_score,
            preview=training.preview,
            presentation=training.presentation,
            info=TrainingInformationBase(
                question_count=training_info.question_count,
                pages_count=training_info.pages_count,
                question=[QuestionResponse(id=q.id, question=q.question) for q in questions]
            ),
        )
        training_responses.append(training_response)

    return training_responses


@router.get("/detail/{training_id}/",
            response_model=TrainingResponse,
            summary="Detail of training",
            description="Fetches detailed information about a specific training")
async def training_detail(training_id: int, db: Session = Depends(get_db)):
    training = db.query(Training).filter(Training.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")

    return training


@router.post("/create/", response_model=TrainingResponse, summary="Create a new training")
def create_new_training(
        module_name: str = Form(...),
        passing_score: int = Form(...),
        pages_count: int = Form(...),
        preview: UploadFile = File(None),
        presentation: UploadFile = File(None),
        questions: List[str] = Form(...),
        db: Session = Depends(get_db),
        request: Request = None
):
    training_info = TrainingInformation(
        question_count=len(questions),
        pages_count=pages_count,
    )

    db.add(training_info)
    db.commit()
    db.refresh(training_info)

    stored_questions = []

    for question_text in questions:
        question_parts = question_text.split(',')
        for part in question_parts:
            trimmed_question = part.strip()
            if trimmed_question:
                create_question = Question(
                    question=trimmed_question,
                    training_information_id=training_info.id
                )
                db.add(create_question)
                stored_questions.append(create_question)

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

    response = TrainingResponse(
        id=new_training.id,
        module_name=new_training.module_name,
        passing_score=new_training.passing_score,
        preview=new_training.preview,
        presentation=new_training.presentation,
        info=TrainingInformationBase(
            question_count=len(stored_questions),
            pages_count=training_info.pages_count,
            question=[QuestionResponse(id=q.id, question=q.question) for q in stored_questions]
        ),
    )

    return response


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
                          user: UserModel = Depends(require_role(1))
                          ):
    training = db.query(Training).filter(Training.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")

    save_preview_location = save_file(preview, request)
    save_presentation_location = save_file(presentation, request)

    training_info = db.query(TrainingInformation).filter(
        TrainingInformation.id == training.training_information).first()

    db.query(Question).filter(Question.training_information_id == training_info.id).delete(synchronize_session=False)
    db.commit()

    for question_text in questions:
        trimmed_question = question_text.strip()
        if trimmed_question:
            create_question = Question(
                question=trimmed_question,
                training_information_id=training_info.id
            )
            db.add(create_question)

    training_info.question_count = len(questions)
    training_info.pages_count = pages_count

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
                              module_name: str = Form(None),
                              passing_score: int = Form(None),
                              pages_count: int = Form(None),
                              preview: UploadFile = File(None),
                              presentation: UploadFile = File(None),
                              questions: List[str] = Form(None),
                              db: Session = Depends(get_db),
                              request: Request = None,
                              user: UserModel = Depends(require_role(TrainType.ADMIN.value))
                              ):
    training = db.query(Training).filter(Training.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")

    if questions is not None:
        training_info = db.query(TrainingInformation).filter(
            TrainingInformation.id == training.training_information).first()
        db.query(Question).filter(Question.training_information_id == training_info.id).delete(
            synchronize_session=False)

        for question_text in questions:
            trimmed_question = question_text.strip()
            if trimmed_question:
                create_question = Question(
                    question=trimmed_question,
                    training_information_id=training_info.id
                )
                db.add(create_question)

        training_info.question_count = len(questions)

    if module_name is not None:
        training.module_name = module_name
    if passing_score is not None:
        training.passing_score = passing_score
    if preview is not None:
        training.preview = save_file(preview, request)
    if presentation is not None:
        training.presentation = save_file(presentation, request)
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
