from datetime import date
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, get_db
from app import models
from app.schedule_logic import generate_schedule

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


@app.post("/admin/generate_schedule")
def api_generate_schedule(
    days: int = 30,
    db: Session = Depends(get_db),
):
    """Generate schedule starting from today for N days ahead."""
    today = date.today()
    created = generate_schedule(db, start_date=today, days_ahead=days)
    return {
        "message": "Schedule generation completed",
        "start_date": str(today),
        "days_ahead": days,
        "duties_created": created,
    }

@app.get("/duties")
def list_duties(
    db: Session = Depends(get_db),
):
    """
    Very simple debug endpoint: list all duties.
    Later we can add filters (by date, etc.).
    """
    duties = (
        db.query(models.Duty)
        .order_by(models.Duty.duty_date.asc(), models.Duty.slot_index.asc())
        .all()
    )

    result = []
    for d in duties:
        result.append(
            {
                "id": d.id,
                "date": str(d.duty_date),
                "slot": d.slot_index,
                "user_id": d.user_id,
                "user_name": d.user.full_name if d.user else None,
                "status": d.status.value if d.status else None,
                "replaced_by_id": d.replaced_by_id,
            }
        )
    return result

