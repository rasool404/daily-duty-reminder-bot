from datetime import date, timedelta
from typing import List, Dict

from sqlalchemy.orm import Session

from app.models import User, Duty, DutyStatus


WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def get_weekday_name(d: date) -> str:
    """Return 'Mon', 'Tue', etc. for a given date."""
    return WEEKDAY_NAMES[d.weekday()]


def parse_work_days(work_days_str: str) -> List[str]:
    """
    Convert 'Mon,Tue,Wed,Thu,Fri' -> ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].
    """
    return [part.strip() for part in work_days_str.split(",") if part.strip()]


def generate_schedule(
    db: Session,
    start_date: date,
    days_ahead: int = 30,
    slots_per_day: int = 2,
) -> int:
    """
    Generate duties from start_date (inclusive) for 'days_ahead' days.

    - Only for active users.
    - Only on days included in each user's work_days.
    - Ensures each day has up to `slots_per_day` people.
    - Tries to balance load by assigning users with the smallest total duties in the range.

    Returns: number of Duty rows created.
    """
    end_date = start_date + timedelta(days=days_ahead)

    # 1) Load all active users
    users: List[User] = db.query(User).filter(User.is_active == True).all()  # noqa: E712
    if not users:
        return 0

    # Map user_id -> workday set (e.g. {"Mon", "Tue", ...})
    user_workdays: Dict[int, set] = {
        u.id: set(parse_work_days(u.work_days)) for u in users
    }

    # 2) Load existing duties in this range so we don't duplicate + we can count loads
    existing_duties: List[Duty] = (
        db.query(Duty)
        .filter(Duty.duty_date >= start_date, Duty.duty_date < end_date)
        .all()
    )

    # user_id -> how many duties in this window
    duty_counts: Dict[int, int] = {u.id: 0 for u in users}
    # date -> list[Duty]
    duties_by_date: Dict[date, List[Duty]] = {}

    for duty in existing_duties:
        duty_counts[duty.user_id] = duty_counts.get(duty.user_id, 0) + 1
        duties_by_date.setdefault(duty.duty_date, []).append(duty)

    created_count = 0

    # 3) Iterate over each day and assign slots
    current = start_date
    while current < end_date:
        weekday_name = get_weekday_name(current)

        # existing duties for this date
        todays_duties = duties_by_date.get(current, [])
        already_assigned_user_ids = {d.user_id for d in todays_duties}

        if len(todays_duties) >= slots_per_day:
            # already fully scheduled
            current += timedelta(days=1)
            continue

        # 3a) eligible users for this date
        eligible_users = [
            u for u in users
            if weekday_name in user_workdays[u.id] and u.id not in already_assigned_user_ids
        ]

        # If not enough eligible users, just fill as many as we can
        free_slots = slots_per_day - len(todays_duties)
        if eligible_users and free_slots > 0:
            # sort by how many duties they already have (fair distribution)
            eligible_users.sort(key=lambda u: (duty_counts.get(u.id, 0), u.id))
            selected_users = eligible_users[:free_slots]

            for idx, user in enumerate(selected_users, start=len(todays_duties) + 1):
                duty = Duty(
                    duty_date=current,
                    slot_index=idx,  # 1, 2, ...
                    user_id=user.id,
                    status=DutyStatus.PLANNED,
                )
                db.add(duty)
                created_count += 1

                # update counters
                duty_counts[user.id] = duty_counts.get(user.id, 0) + 1
                duties_by_date.setdefault(current, []).append(duty)

        current += timedelta(days=1)

    db.commit()
    return created_count
