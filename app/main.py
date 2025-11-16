from fastapi import FastAPI
from app.api.api_v1 import api_router as api_router_v1
from app.db.session import engine
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Nullbane Backend")

AVATAR_VOLUME_PATH = "/data/avatars"
os.makedirs(AVATAR_VOLUME_PATH, exist_ok=True)
app.mount("/static/avatars", StaticFiles(directory=AVATAR_VOLUME_PATH), name="avatars")

app.include_router(api_router_v1, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Bienvenido a Nullbane API"}
