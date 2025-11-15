from fastapi import FastAPI
from app.api.api_v1 import api_router as api_router_v1


app = FastAPI(title="Nullbane Backend")

app.include_router(api_router_v1, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Bienvenido a Nullbane API"}