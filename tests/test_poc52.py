"""One independent executable POC harness check per master POC identifier."""
import pytest
from mt_iam.poc.registry import BY_ID, CASES
from mt_iam.poc.checks import CHECKS, EXTERNAL, inventory_is_complete
from mt_iam.poc.runner import execute, main

@pytest.mark.parametrize("case", CASES, ids=lambda c: c.id)
def test_poc_check_or_explicit_blocker(case):
    result = execute(case.id)
    assert result.id == case.id
    assert result.status in {"LOCAL_CHECK_PASS", "BLOCKED"}, result
    if result.status == "BLOCKED":
        assert len(result.detail) > 35
    if result.status == "LOCAL_CHECK_PASS":
        assert result.duration_ms is not None


def test_exact_registry_and_no_fake_green():
    inventory_is_complete()
    assert len(BY_ID) == 52
    assert set(CHECKS).isdisjoint(EXTERNAL)
    assert "POC-G05-06" in EXTERNAL  # Conformance must remain blocked until truly run.
    assert "POC-G02-01" in EXTERNAL  # SQLite must not count as Supabase evidence.


def test_release_gate_fails_closed(tmp_path):
    report = tmp_path / "evidence.json"
    assert main(["--output", str(report), "--require-all-pass"]) == 1
    assert report.is_file()
