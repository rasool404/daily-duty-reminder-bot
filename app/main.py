from fastapi import FastAPI
from app.config import settings
from app.database import engine
from app import models

app = FastAPI(title="Navbatchilik Bot Dashboard")


# This will create tables if they don't exist yet
@app.on_event("startup")
def on_startup():
    print("Creating database tables (if not exists)...")
    models.Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {
        "message": "Navbatchilik bot dashboard backend running",
        "env": settings.ENVIRONMENT,
    }
