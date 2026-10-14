"""
DataPulse - Shared Test Configuration & Fixtures.

Provides:
- Isolated test database preventing modification of real data/datapulse.db
- Authenticated headers fixture using the real registration/login API flow
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from db.connection import get_engine, init_db


@pytest.fixture(scope="session", autouse=True)
def isolated_test_database(tmp_path_factory: pytest.TempPathFactory) -> Generator[Path, None, None]:
    """
    Provide an isolated test database in a temporary directory.
    Ensures tests never modify the real development or production database.
    """
    temp_dir = tmp_path_factory.mktemp("datapulse_test_db")
    test_db_path = temp_dir / "datapulse_test.db"

    source_db = Path("data/datapulse.db")
    if source_db.exists():
        shutil.copy(source_db, test_db_path)
    else:
        from db.load_data import load_clean_data_to_db
        load_clean_data_to_db(db_url=f"sqlite:///{test_db_path.resolve()}")

    test_db_url = f"sqlite:///{test_db_path.resolve()}"
    old_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = test_db_url

    # Ensure all tables exist in the isolated test database
    engine = get_engine(test_db_url)
    init_db(engine)

    yield test_db_path

    # Teardown: close engine connections and restore environment
    engine.dispose()
    if old_db_url is not None:
        os.environ["DATABASE_URL"] = old_db_url
    else:
        os.environ.pop("DATABASE_URL", None)


@pytest.fixture(scope="session")
def auth_headers(isolated_test_database: Path) -> Dict[str, str]:
    """
    Authenticate via the existing registration/login API mechanism
    and return authorization headers with a valid Bearer JWT.
    """
    with TestClient(app) as test_client:
        user_credentials = {
            "email": "test_runner@example.com",
            "password": "TestPassword123!",
        }

        # Attempt registration (201 Created or 409 Conflict if already present)
        reg_response = test_client.post(
            "/api/auth/register",
            json={
                "email": user_credentials["email"],
                "full_name": "Test Runner",
                "password": user_credentials["password"],
            },
        )
        assert reg_response.status_code in (201, 409), (
            f"Registration failed in test setup: {reg_response.text}"
        )

        # Login to obtain access token
        login_response = test_client.post(
            "/api/auth/login",
            json=user_credentials,
        )
        assert login_response.status_code == 200, (
            f"Login failed in test setup: {login_response.text}"
        )

        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
