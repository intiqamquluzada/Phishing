from sqlalchemy.orm import Session
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from phish.dependencies import get_db
from phish.models.email import EmailTemplate
from phish.schemas.email import (EmailDifficulty, EmailTemplateBase, EmailTemplateResponse)
from enum import Enum as PyEnum
from fastapi.responses import JSONResponse
import shutil
import os
from phish.utils.generator import generate_short_uuid


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
                          db: Session = Depends(get_db)):

    if file:
        folder_path = "./upload_files/template/"
        os.makedirs(folder_path, exist_ok=True)
        file_location = os.path.join(folder_path, f"{generate_short_uuid()}-{file.filename}")

        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

    new_template = EmailTemplate(
        name=name,
        description=description,
        difficulty=difficulty.value,
        subject=subject,
        body=body,
        file_path=file_location if file else None
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
                          db: Session = Depends(get_db)):
    upt_template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()

    if not upt_template:
        raise HTTPException(status_code=404, detail="Template not found")

    if file:
        folder_path = "./upload_files/template/"
        os.makedirs(folder_path, exist_ok=True)
        file_location = os.path.join(folder_path, f"{generate_short_uuid()}-{file.filename}")

        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        upt_template.file_path = file_location

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
                                db: Session = Depends(get_db)):
    upt_template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()

    if not upt_template:
        raise HTTPException(status_code=404, detail="Template not found")

    upt_template.name = name
    upt_template.description = description
    upt_template.difficulty = difficulty.value
    upt_template.subject = subject
    upt_template.body = body

    if file:
        folder_path = "./upload_files/template/"
        os.makedirs(folder_path, exist_ok=True)
        file_location = os.path.join(folder_path, f"{generate_short_uuid()}-{file.filename}")

        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        upt_template.file_path = file_location

    db.commit()
    db.refresh(upt_template)

    return upt_template


@router.delete("/delete/{template_id",
               summary="Update template",
               description="Update template")
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
