"""Application settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    llm_mode: str = "mock"  # mock | qwen
    dashscope_api_key: str = ""
    dashscope_model: str = "qwen-plus"
    # Workspace OpenAI-compatible base (Beijing Model Studio). No trailing slash required.
    dashscope_base_url: str = (
        "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    )
    database_url: str = "sqlite:///./data/relief.db"
    # LangGraph HITL checkpoints (SQLite file path when using SQLite; unused for Postgres)
    checkpoint_path: str = ""
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        if origins == ["*"]:
            return ["*"]
        return origins

    @property
    def is_postgres(self) -> bool:
        url = self.database_url.lower()
        return url.startswith("postgresql") or url.startswith("postgres")

    @property
    def sqlalchemy_url(self) -> str:
        """Normalize DATABASE_URL for SQLAlchemy."""
        url = self.database_url
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://") :]
        if url.startswith("postgresql://") and "+psycopg" not in url:
            return "postgresql+psycopg://" + url[len("postgresql://") :]
        return url

    @property
    def psycopg_url(self) -> str:
        """Plain postgresql:// URL for LangGraph / psycopg."""
        url = self.database_url
        if "+psycopg" in url:
            url = url.replace("postgresql+psycopg://", "postgresql://", 1)
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]
        return url

    @property
    def db_path(self) -> Path:
        if self.database_url.startswith("sqlite:///"):
            return Path(self.database_url.replace("sqlite:///", ""))
        return Path("./data/relief.db")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
