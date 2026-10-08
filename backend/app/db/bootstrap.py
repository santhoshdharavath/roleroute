from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.seed.loader import seed_database


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
