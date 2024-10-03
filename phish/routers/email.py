from sqlalchemy.orm import Session
from fastapi import (APIRouter, Depends, HTTPException, Form,
                     UploadFile, File, Request)
from fastapi.responses import JSONResponse
from phish.dependencies import get_db
from phish.models.email import EmailTemplate
from phish.schemas.email import (EmailDifficulty, EmailTemplateBase, EmailTemplateResponse)
from phish.utils.generator import generate_short_uuid
from phish.utils.files import save_file
from enum import Enum as PyEnum
from typing import List
import shutil
import os

router = APIRouter(
    prefix="/email-templates",
    tags=["Email Templates"]
)

@router.get("/",
            response_model=List[EmailTemplateResponse],
            summary="List of email templates",
            description="List of email templates")
async def email_template_list(db: Session = Depends(get_db)):
    templates = db.query(EmailTemplate).all()

    if not templates:
        raise HTTPException(status_code=404, detail="Email template not found")

    return templates


@router.get("/detail/{template_id}",
            response_model=EmailTemplateResponse,
            summary="Detail of email templates",
            description="Detail of email templates")
async def email_template_list(template_id: int, db: Session = Depends(get_db)):
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.post("/create/",
             response_model=EmailTemplateResponse,
             summary="Create a new template")
async def create_template(name: str = Form(...),
                          description: str = Form(...),
                          difficulty: EmailDifficulty = Form(...),
                          subject: str = Form(...),
                          body: str = Form(...),
                          file: UploadFile = File(None),
                          request: Request = None,
                          db: Session = Depends(get_db)):

    save_location = save_file(file, request)

    new_template = EmailTemplate(
        name=name,
        description=description,
        difficulty=difficulty.value,
        subject=subject,
        body=body,
        file_path=save_location if file else None
    )

    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return new_template


@router.put("/update/{template_id}",
            response_model=EmailTemplateResponse,
            summary="Update template",
            description="Update template")
async def update_template(template_id: int,
                          name: str = Form(...),
                          description: str = Form(...),
                          difficulty: EmailDifficulty = Form(...),
                          subject: str = Form(...),
                          body: str = Form(...),
                          file: UploadFile = File(None),
                          request: Request = None,
                          db: Session = Depends(get_db)):
    upt_template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()

    if not upt_template:
        raise HTTPException(status_code=404, detail="Template not found")

    save_location = save_file(file, request)

    if save_location:
        upt_template.file_path = save_location

    upt_template.name = name
    upt_template.description = description
    upt_template.difficulty = difficulty.value
    upt_template.subject = subject
    upt_template.body = body

    db.commit()
    db.refresh(upt_template)

    return upt_template


@router.patch("/update/{template_id}",
              response_model=EmailTemplateResponse,
              summary="Update template",
              description="Update template")
async def update_template_patch(template_id: int,
                                name: str = Form(None),
                                description: str = Form(None),
                                difficulty: EmailDifficulty = Form(None),
                                subject: str = Form(None),
                                body: str = Form(None),
                                file: UploadFile = File(None),
                                request: Request = None,
                                db: Session = Depends(get_db)):
    upt_template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()

    if not upt_template:
        raise HTTPException(status_code=404, detail="Template not found")

    if name is not None:
        upt_template.name = name
    if description is not None:
        upt_template.description = description
    if difficulty is not None:
        upt_template.difficulty = difficulty.value
    if subject is not None:
        upt_template.subject = subject
    if body is not None:
        upt_template.body = body

    save_location = save_file(file, request)

    if save_location:
        upt_template.file_path = save_location

    db.commit()
    db.refresh(upt_template)

    return upt_template


@router.delete("/delete/{template_id",
               summary="Delete template",
               description="Delete template")
async def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    db.delete(template)
    db.commit()

    content = {
        "message": "Template deleted successfully"
    }

    return JSONResponse(status_code=200, content=content)
