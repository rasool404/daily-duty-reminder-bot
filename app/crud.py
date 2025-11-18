from typing import Optional

from sqlalchemy.orm import Session
from aiogram.types import User as TgUser

from app import models
from app.models import User


def get_user_by_tg_id(db: Session, tg_id: int) -> Optional[User]:
    return db.query(User).filter(User.tg_id == tg_id).first()


def create_user_from_telegram(db: Session, tg_user: TgUser) -> User:
    """
    Create a new User row based on Telegram user.
    Default work_days = Mon-Fri.
    """
    full_name = tg_user.full_name or (tg_user.first_name or "").strip()
    username = tg_user.username

    user = User(
        tg_id=tg_user.id,
        tg_username=username,
        full_name=full_name or username or f"User {tg_user.id}",
        work_days="Mon,Tue,Wed,Thu,Fri",
        is_active=True,
    )
    db.add(user)
    return user


def upsert_user_from_telegram(db: Session, tg_user: TgUser) -> User:
    """
    If user with this tg_id exists → update username/full_name.
    If not → create a new one.
    """
    user = get_user_by_tg_id(db, tg_user.id)
    full_name = tg_user.full_name or (tg_user.first_name or "").strip()
    username = tg_user.username

    if user is None:
        user = create_user_from_telegram(db, tg_user)
    else:
        # Update info in case user changed username/name
        user.tg_username = username
        if full_name:
            user.full_name = full_name

    return user
