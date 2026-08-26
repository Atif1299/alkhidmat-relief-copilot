"""Database session and engine."""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db.models import Base

_db_file = settings.db_path
_db_file.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{_db_file.as_posix()}",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    # Lightweight SQLite migrations for Tier B columns
    with engine.begin() as conn:
        tables = {
            row[0]
            for row in conn.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        if "cases" in tables:
            cols = {
                row[1]
                for row in conn.exec_driver_sql("PRAGMA table_info(cases)").fetchall()
            }
            if "sop_hits" not in cols:
                conn.exec_driver_sql("ALTER TABLE cases ADD COLUMN sop_hits JSON")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
