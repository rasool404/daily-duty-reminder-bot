from datetime import datetime, date
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship

from app.database import Base


class DutyStatus(str, enum.Enum):
    PLANNED = "planned"
    CONFIRMED = "confirmed"
    REPLACED = "replaced"
    MISSED = "missed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # We'll fill tg_id/username when they DM /start
    tg_id = Column(Integer, index=True, nullable=True, unique=True)
    tg_username = Column(String, index=True, nullable=True)

    full_name = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    # Store work days as a comma-separated string for simplicity: "Mon,Tue,Wed,Thu,Fri"
    work_days = Column(String, nullable=False, default="Mon,Tue,Wed,Thu,Fri")

    created_at = Column(DateTime, default=datetime.utcnow)

    duties = relationship("Duty", back_populates="user", foreign_keys="Duty.user_id")
    replaced_duties = relationship(
        "Duty",
        back_populates="replaced_by",
        foreign_keys="Duty.replaced_by_id",
    )

    def __repr__(self):
        return f"<User id={self.id} name={self.full_name!r}>"


class Duty(Base):
    __tablename__ = "duties"

    id = Column(Integer, primary_key=True, index=True)

    duty_date = Column(Date, index=True, nullable=False)
    # 1 or 2 (two people per day), might be extended later
    slot_index = Column(Integer, nullable=False, default=1)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="duties", foreign_keys=[user_id])

    status = Column(Enum(DutyStatus), default=DutyStatus.PLANNED, nullable=False)

    replaced_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    replaced_by = relationship(
        "User", back_populates="replaced_duties", foreign_keys=[replaced_by_id]
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self):
        return f"<Duty id={self.id} date={self.duty_date} slot={self.slot_index} user_id={self.user_id}>"
