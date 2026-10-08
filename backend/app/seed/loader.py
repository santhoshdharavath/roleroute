import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.internship import Internship
from app.models.learning import Module, Role, Topic
from app.models.user import User

SEED_DIR = Path(__file__).resolve().parent


def _read_json(name: str) -> list[dict]:
    with (SEED_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def seed_database(db: Session) -> None:
    settings = get_settings()

    if db.get(Role, 1) is None:
        for item in _read_json("roles.json"):
            db.add(Role(**item))
        for item in _read_json("modules.json"):
            db.add(Module(**item))
        for item in _read_json("topics.json"):
            db.add(Topic(**item))
        for item in _read_json("internships.json"):
            db.add(Internship(**item))
        db.flush()

    demo_user = db.get(User, settings.demo_user_id)
    if demo_user is None:
        db.add(
            User(
                id=settings.demo_user_id,
                name=settings.demo_user_name,
                email=settings.demo_user_email,
                selected_role_id=None,
                target_date=None,
            )
        )

    db.commit()
