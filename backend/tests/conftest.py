# pytest configuration — SQLite + auth for tests
import os
import sys
from pathlib import Path

# Must set before importing app.*
# Non-empty DASHSCOPE_API_KEY wins over .env (env_ignore_empty skips "").
os.environ["DATABASE_URL"] = "sqlite:///./data/test_tier3.db"
os.environ["LLM_MODE"] = "mock"
os.environ["AUTH_DISABLED"] = "false"
os.environ["JWT_SECRET"] = "test-jwt-secret-aiddesk-tier3-32chars"
os.environ["DASHSCOPE_API_KEY"] = "__tests_no_dashscope__"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    from app.config import get_settings

    get_settings.cache_clear()
    import app.config as config_mod
    import app.db.session as session_mod
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Mutate the shared settings object in place so other modules' `settings` aliases update.
    config_mod.settings = get_settings()
    s = config_mod.settings
    s.dashscope_api_key = ""
    s.llm_mode = "mock"
    s.auth_disabled = False
    s.database_url = "sqlite:///./data/test_tier3.db"

    Path("./data").mkdir(parents=True, exist_ok=True)
    test_db = Path("./data/test_tier3.db")
    if session_mod.engine is not None:
        session_mod.engine.dispose()
    if test_db.exists():
        try:
            test_db.unlink()
        except PermissionError:
            # Fall back to a fresh file if Windows still locks the old one.
            test_db = Path("./data/test_tier3_session.db")
            s.database_url = f"sqlite:///{test_db.as_posix()}"
            if test_db.exists():
                try:
                    test_db.unlink()
                except PermissionError:
                    pass

    session_mod.engine = create_engine(
        f"sqlite:///{test_db.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    session_mod.SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=session_mod.engine
    )

    from app.db.seed import run_seed
    from app.db.session import init_db
    from app.main import app

    init_db()
    run_seed()
    with TestClient(app) as test_client:
        yield test_client
    session_mod.engine.dispose()


@pytest.fixture(scope="session")
def auth_headers(client):
    """Supervisor token for full API access."""
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "supervisor@aiddesk.example", "password": "AidDesk!2026"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def citizen_headers(client):
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "citizen@aiddesk.example", "password": "AidDesk!2026"},
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="session")
def desk_headers(client):
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "desk@aiddesk.example", "password": "AidDesk!2026"},
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
