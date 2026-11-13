import pytest
from sqlalchemy import text
from mt_iam.adapters.database import Database
from mt_iam.api.app import create_app
from mt_iam.core.config import Settings
from fastapi.testclient import TestClient

def test_sqlite_smoke_with_explicit_test_driver(tmp_path):
    db = Database(f"sqlite+pysqlite:///{tmp_path/'synthetic.sqlite'}")
    try:
        assert db.ping()
        with db.session() as s:
            s.execute(text("CREATE TABLE synthetic (id INTEGER PRIMARY KEY, name TEXT)"))
        with db.session() as s:
            s.execute(text("INSERT INTO synthetic (name) VALUES ('mock')"))
        with db.session() as s:
            assert s.execute(text("SELECT name FROM synthetic")).scalar_one() == "mock"
    finally:
        db.dispose()

def test_exception_rolls_back(tmp_path):
    db = Database(f"sqlite+pysqlite:///{tmp_path/'rollback.sqlite'}")
    try:
        with db.session() as s:
            s.execute(text("CREATE TABLE synthetic (id INTEGER PRIMARY KEY, name TEXT)"))
        with pytest.raises(RuntimeError):
            with db.session() as s:
                s.execute(text("INSERT INTO synthetic (name) VALUES ('should-rollback')"))
                raise RuntimeError("synthetic failure")
        with db.session() as s:
            assert s.execute(text("SELECT COUNT(*) FROM synthetic")).scalar_one() == 0
    finally:
        db.dispose()

def test_reject_unapproved_driver():
    with pytest.raises(ValueError):
        Database("mysql://localhost:3306/test")

def test_lifespan_disposes_engine(tmp_path):
    app = create_app(Settings(environment="test",database_url=f"sqlite+pysqlite:///{tmp_path/'db.sqlite'}"))
    with TestClient(app) as client:
        assert client.get("/health/ready").status_code == 200
        db=app.state.database
        assert db.ping()
    assert app.state.ready is False
