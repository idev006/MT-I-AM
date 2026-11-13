"""Evidence hashing checks fail closed on path and data attacks."""
import hashlib
import json

import pytest

from mt_iam.poc.artifact_integrity import MAX_ARTIFACT_BYTES, verify_artifacts
from mt_iam.poc.quality_gate import main as quality_main


def evidence(name, digest):
    return {"artifacts": [{"path": name, "sha256": digest}]}


def test_valid_bytes(tmp_path):
    (tmp_path / "proof.log").write_bytes(b"bounded synthetic proof")
    digest = hashlib.sha256(b"bounded synthetic proof").hexdigest()
    audit = verify_artifacts(evidence("proof.log", digest), tmp_path)
    assert audit.verified and audit.files_checked == 1


def test_tampered_bytes(tmp_path):
    (tmp_path / "proof.log").write_bytes(b"changed")
    assert not verify_artifacts(evidence("proof.log", "a" * 64), tmp_path).verified


@pytest.mark.parametrize("name", ["../secret", "/etc/passwd", "..\\secret", "C:/Windows/win.ini", "x/./f"])
def test_path_attacks(tmp_path, name):
    assert not verify_artifacts(evidence(name, "a" * 64), tmp_path).verified


def test_symlink_outside_root(tmp_path):
    outside = tmp_path.parent / "outside-proof.txt"
    outside.write_text("forbidden")
    (tmp_path / "escape").symlink_to(outside)
    assert not verify_artifacts(
        evidence("escape", hashlib.sha256(b"forbidden").hexdigest()), tmp_path
    ).verified


def test_duplicate_path(tmp_path):
    (tmp_path / "a").write_text("content")
    item = {"path": "a", "sha256": hashlib.sha256(b"content").hexdigest()}
    assert not verify_artifacts({"artifacts": [item, item]}, tmp_path).verified


def test_large_file_rejected(tmp_path):
    with (tmp_path / "large").open("wb") as file:
        file.truncate(MAX_ARTIFACT_BYTES + 1)
    assert not verify_artifacts(evidence("large", "a" * 64), tmp_path).verified


def test_special_file_rejected(tmp_path):
    assert not verify_artifacts(evidence(".", "a" * 64), tmp_path).verified


def test_missing_root_rejected(tmp_path):
    assert not verify_artifacts(evidence("proof", "a" * 64), tmp_path / "missing").verified


def test_cli_fail_closed_without_artifact_root(tmp_path):
    payload = {
        "poc_id": "POC-G10-01", "schema_version": 1, "verification_status": "PASS",
        "runner_status": "LOCAL_CHECK_PASS", "external_or_scope_evidence": "VERIFIED",
        "source_sha": "a" * 40, "environment": "Synthetic Linux test",
        "command": "python -m pytest", "owner": "owner",
        "reviewer": "independent", "review_decision": "ACCEPT",
        "resource_cleanup": "VERIFIED",
        "cases": [{"kind": "positive", "status": "PASS"}, {"kind": "negative", "status": "PASS"}],
        "artifacts": [{"path": "proof", "sha256": "a" * 64}],
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(payload))
    assert quality_main([str(path)]) == 2
