from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from .routers import users, training, email, target, administration, role

app = FastAPI()

upload_folder = 'api/static'
os.makedirs(upload_folder, exist_ok=True)

static_router = APIRouter()

@static_router.get("/static/{image_name}", tags=['Image selector'])
async def get_image(image_name: str):
    image_path = os.path.join(upload_folder, image_name)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)

app.mount("/static", StaticFiles(directory=upload_folder), name="static")

app.include_router(users.router)
app.include_router(training.router)
app.include_router(email.router)
app.include_router(target.router)
app.include_router(administration.router)
app.include_router(role.router)

app.include_router(static_router, prefix="/api")
