"""Database session and engine."""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db.models import Base


def _make_engine():
    if settings.is_postgres:
        return create_engine(
            settings.sqlalchemy_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=5,
        )
    db_file = settings.db_path
    db_file.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )


engine = _make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    if settings.is_postgres:
        return
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
