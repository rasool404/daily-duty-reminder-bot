from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, get_db
from app import models

app = FastAPI(title="Navbatchilik Bot Dashboard")


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


@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    # Manually serialize to avoid issues
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "tg_id": u.tg_id,
            "tg_username": u.tg_username,
            "work_days": u.work_days,
            "is_active": u.is_active,
        }
        for u in users
    ]
