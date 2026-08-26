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
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def db_path(self) -> Path:
        if self.database_url.startswith("sqlite:///"):
            return Path(self.database_url.replace("sqlite:///", ""))
        return Path("./data/relief.db")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
