from typing import Union
from fastapi import FastAPI
from .routers import users, training, email, target

app = FastAPI()
app.include_router(users.router)
app.include_router(training.router)
app.include_router(email.router)
app.include_router(target.router)

