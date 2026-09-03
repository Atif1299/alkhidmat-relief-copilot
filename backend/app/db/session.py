"""Database session and engine — Postgres target; SQLite legacy for tests."""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, text
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
            connect_args={"connect_timeout": 5},
        )
    db_file = settings.db_path
    db_file.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )


engine = _make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _ensure_postgres_schema() -> None:
    """Migrate existing Cloud SQL tables + enable pgvector when available."""
    dim = int(settings.embedding_dim)
    with engine.begin() as conn:
        # Tier 3 portable embeddings on existing sop_chunks rows
        conn.execute(
            text(
                """
                DO $$
                BEGIN
                  IF EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_name = 'sop_chunks'
                  ) AND NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'sop_chunks' AND column_name = 'embedding'
                  ) THEN
                    ALTER TABLE sop_chunks ADD COLUMN embedding JSON;
                  END IF;
                END $$;
                """
            )
        )
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.execute(
                text(
                    f"""
                    DO $$
                    BEGIN
                      IF EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = 'sop_chunks'
                      ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'sop_chunks' AND column_name = 'embedding_vec'
                      ) THEN
                        ALTER TABLE sop_chunks ADD COLUMN embedding_vec vector({dim});
                      END IF;
                    END $$;
                    """
                )
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[startup] pgvector setup skipped: {exc}")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    if settings.is_postgres:
        try:
            _ensure_postgres_schema()
        except Exception as exc:  # noqa: BLE001
            print(f"[startup] postgres schema migrate skipped: {exc}")
        return
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
        if "sop_chunks" in tables:
            cols = {
                row[1]
                for row in conn.exec_driver_sql("PRAGMA table_info(sop_chunks)").fetchall()
            }
            if "embedding" not in cols:
                conn.exec_driver_sql("ALTER TABLE sop_chunks ADD COLUMN embedding JSON")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
