from fastapi import (APIRouter, Depends, HTTPException, Form, UploadFile, File, Request, WebSocket, WebSocketDisconnect)
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4

from phish.dependencies import get_db, ConnectionManager
from phish.external_services.inject_tracking import inject_tracking_pixel_and_links
from phish.models.email import EmailTemplate, EmailReadEvent
from phish.schemas.email import EmailDifficulty, EmailTemplateResponse
from phish.utils.email_sender import send_email_with_tracking
from phish.utils.files import save_file

router = APIRouter(
    prefix="/email-templates",
    tags=["Email Templates"]
)

manager = ConnectionManager()
@router.websocket("/ws/email-tracker")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)  # Use connection manager to handle WebSocket connections
    try:
        while True:
            await websocket.receive_text()  # You can handle incoming WebSocket messages here if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)




@router.get("/",
            response_model=List[EmailTemplateResponse],
            summary="List of email templates")
async def email_template_list(db: Session = Depends(get_db)):
    templates = db.query(EmailTemplate).all()
    if not templates:
        raise HTTPException(status_code=404, detail="Email template not found")
    return templates


@router.get("/detail/{template_id}",
            response_model=EmailTemplateResponse,
            summary="Detail of email templates")
async def email_template_detail(template_id: int, db: Session = Depends(get_db)):
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
    unique_uuid = str(uuid4())

    new_template = EmailTemplate(
        name=name,
        description=description,
        difficulty=difficulty.value,
        subject=subject,
        body=body,
        file_path=save_location if file else None
    )

    # Inject the tracking pixel
    new_template.body = inject_tracking_pixel_and_links(new_template.body, new_template.id, unique_uuid)

    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return new_template


@router.put("/update/{template_id}",
            response_model=EmailTemplateResponse,
            summary="Update template")
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
              summary="Partially update template")
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


@router.delete("/delete/{template_id}",
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


from fastapi import Query
from fastapi.responses import RedirectResponse


@router.post("/send/{template_id}")
async def send_template_email(template_id: int, recipients: List[str], db: Session = Depends(get_db)):
    unique_uuid = str(uuid4())
    print("UNIQUE ID: ", unique_uuid)
    await manager.broadcast("Yolladig brat")

    try:
        await send_email_with_tracking(template_id, db, recipients, unique_uuid)
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/track/{template_id}")
async def track_email_read(template_id: int, uuid: str, db: Session = Depends(get_db)):
    print(f"Tracking pixel triggered for template {template_id} with UUID {uuid}")  # Debug

    email_read_event = EmailReadEvent(template_id=template_id, uuid=uuid)
    db.add(email_read_event)
    db.commit()

    await manager.broadcast(f"Email template {template_id} was opened (UUID: {uuid})")

    transparent_pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4C\x01\x00\x3B'
    return Response(content=transparent_pixel, media_type="image/gif")





@router.get("/click/{template_id}")
async def track_link_click(template_id: int, uuid: str, url: str, db: Session = Depends(get_db)):
    await manager.broadcast(f"Email template {template_id} link clicked (UUID: {uuid}) URL: {url}")

    return RedirectResponse(url=url)