"""Deterministic local tests for the Python foundation (POC-G10-01/G01-01 partial)."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from fastapi.testclient import TestClient

from mt_iam.api.app import create_app
from mt_iam.core.config import Settings
from mt_iam.core.paths import PathManager


def test_health_and_lifespan() -> None:
    app = create_app(Settings(environment="test"))
    with TestClient(app) as client:
        assert client.get("/health/live").json() == {"status": "alive"}
        assert client.get("/health/ready").json() == {"status": "ready"}
    assert app.state.ready is False


def test_path_manager_rejects_traversal() -> None:
    manager = PathManager(Path("/tmp/poc-root"))
    with pytest.raises(ValueError):
        manager.project_file("../secrets")
    with pytest.raises(ValueError):
        manager.project_file("/etc/passwd")


def test_scoped_temp_files_are_removed() -> None:
    with TemporaryDirectory() as root:
        with PathManager.scratch() as scratch:
            target = Path(scratch)
            (target / "case.txt").write_text("synthetic")
            assert target.exists()
        assert not target.exists()


def test_production_disables_docs() -> None:
    app = create_app(Settings(environment="production"))
    with TestClient(app) as client:
        assert client.get("/docs").status_code == 404
