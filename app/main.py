from fastapi import FastAPI
from app.api.api_v1 import api_router as api_router_v1
from app.db.session import engine
from fastapi.staticfiles import StaticFiles
import os

from app.modules.users import model as user_model
from app.modules.settings import model as settings_model
from app.modules.posts import model as post_model
from app.modules.comments import model as comment_model
from app.modules.friendships import model as friendship_model
from app.modules.chat import model as message_model
from app.modules.achievements import model as achievement_model

app = FastAPI(title="Nullbane Backend")

AVATAR_VOLUME_PATH = "/data/avatars"
os.makedirs(AVATAR_VOLUME_PATH, exist_ok=True)
app.mount("/static/avatars", StaticFiles(directory=AVATAR_VOLUME_PATH), name="avatars")

app.include_router(api_router_v1, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Bienvenido a Nullbane API"}
