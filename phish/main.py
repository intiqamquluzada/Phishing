from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from .routers import users, training, email, target, administration, role
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .routers.email import manager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("Client connected")
    try:
        while True:
            message = await websocket.receive_text()
            print(f"Message received: {message}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")


app.include_router(users.router)
app.include_router(training.router)
app.include_router(email.router)
app.include_router(target.router)
app.include_router(administration.router)
app.include_router(role.router)

app.include_router(static_router, prefix="/api")