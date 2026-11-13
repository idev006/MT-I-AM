from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
from fastapi.testclient import TestClient
from mt_iam.api.app import create_app
from mt_iam.core.config import Settings
from mt_iam.core.paths import PathManager

def test_health_and_lifespan():
    app = create_app(Settings(environment="test"))
    with TestClient(app) as client:
        assert client.get("/health/live").json() == {"status": "alive"}
        assert client.get("/health/ready").json() == {"status": "ready"}
    assert app.state.ready is False

def test_path_manager_rejects_traversal():
    manager = PathManager(Path("/tmp/poc-root"))
    with pytest.raises(ValueError):
        manager.project_file("../secrets")
    with pytest.raises(ValueError):
        manager.project_file(str(Path.cwd().anchor + "outside-root"))

def test_scoped_temp_files_are_removed():
    with TemporaryDirectory() as _:
        with PathManager.scratch() as scratch:
            target = Path(scratch)
            (target / "case.txt").write_text("synthetic")
            assert target.exists()
        assert not target.exists()

def test_production_requires_https_issuer():
    with pytest.raises(ValueError):
        Settings(environment="production")
    app = create_app(Settings(environment="production", issuer_url="https://iam.example.test"))
    with TestClient(app) as client:
        assert client.get("/docs").status_code == 404
