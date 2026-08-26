# pytest configuration
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(scope="module")
def client():
    from app.db.seed import run_seed
    from app.db.session import init_db
    from app.main import app

    init_db()
    run_seed()
    with TestClient(app) as test_client:
        yield test_client
