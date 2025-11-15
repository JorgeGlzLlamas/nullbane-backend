from fastapi import FastAPI
from app.api.api_v1 import api_router as api_router_v1
from app.db.session import engine
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Nullbane Backend")

os.makedirs("static", exist_ok=True)
app.mount("/static/avatars", StaticFiles(directory="/data/avatars"), name="avatars")

app.include_router(api_router_v1, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Bienvenido a Nullbane API"}
