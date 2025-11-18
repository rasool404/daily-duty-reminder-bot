from fastapi import FastAPI
from app.config import settings

app = FastAPI(title="Navbatchilik Bot Dashboard")


@app.get("/")
def read_root():
    return {
        "message": "Navbatchilik bot dashboard backend running",
        "env": settings.ENVIRONMENT,
    }
