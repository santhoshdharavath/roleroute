from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.user import User


def current_settings() -> Settings:
    return get_settings()


def get_demo_user(db: Session = Depends(get_db), settings: Settings = Depends(current_settings)) -> User:
    user = db.get(User, settings.demo_user_id)
    if user is None:
        raise HTTPException(status_code=500, detail="Demo user is missing. Restart the API to reseed.")
    return user
