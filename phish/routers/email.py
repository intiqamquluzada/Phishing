from sqlalchemy.orm import Session
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from phish.dependencies import get_db
from phish.models.email import EmailTemplate
from phish.schemas.email import (EmailTemplateBase, EmailTemplateResponse, EmailTemplatePatch)
from enum import Enum as PyEnum


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
async def create_template(template: EmailTemplateBase, db: Session = Depends(get_db)):
    new_template = EmailTemplate(
        name=template.name,
        description=template.description,
        difficulty=template.difficulty.value,
        type=template.type.value,
        payload_type=template.payload_type,
        subject=template.subject,
        body=template.body
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
                          template: EmailTemplateBase,
                          db: Session = Depends(get_db)):
    upt_template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()

    if not upt_template:
        raise HTTPException(status_code=404, detail="Template not found")

    upt_template.name = template.name
    upt_template.description = template.description
    upt_template.difficulty = template.difficulty.value
    upt_template.type = template.type.value
    upt_template.payload_type = template.payload_type
    upt_template.subject = template.subject
    upt_template.body = template.body

    db.commit()
    db.refresh(upt_template)

    return upt_template


@router.put("/update/{template_id}",
            response_model=EmailTemplateResponse,
            summary="Update template",
            description="Update template")
async def update_template(template_id: int,
                          template: EmailTemplateBase,
                          db: Session = Depends(get_db)):
    upt_template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()

    if not upt_template:
        raise HTTPException(status_code=404, detail="Template not found")

    upt_template.name = template.name
    upt_template.description = template.description
    upt_template.difficulty = template.difficulty.value
    upt_template.type = template.type.value
    upt_template.payload_type = template.payload_type
    upt_template.subject = template.subject
    upt_template.body = template.body

    db.commit()
    db.refresh(upt_template)

    return upt_template


@router.patch("/update/{template_id}",
              response_model=EmailTemplateResponse,
              summary="Update template",
              description="Update template")
async def update_template_patch(template_id: int,
                                template: EmailTemplatePatch,
                                db: Session = Depends(get_db)):
    upt_template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()

    if not upt_template:
        raise HTTPException(status_code=404, detail="Template not found")

    update_data = template.dict(exclude_unset=True)

    for key, value in update_data.items():
        if isinstance(value, PyEnum):
            value = value.value
        setattr(upt_template, key, value)

    db.commit()
    db.refresh(upt_template)

    return upt_template
