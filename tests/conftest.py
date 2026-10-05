import pytest

import database.db as database
from app import create_app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    test_database = tmp_path / "test_academic.db"

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        test_database,
    )

    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client
