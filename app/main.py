from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

from app.db.session import engine
from app.modules.users import model


app = FastAPI(title="Backend for Nullbane")


@app.get("/")
def read_root():
    return {"status": "ok"}