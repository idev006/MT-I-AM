"""Repeatability contracts: deterministic drift detection, no false full PASS."""
import pytest
from mt_iam.poc import repeatability
from mt_iam.poc.platform import POCRegistry, RunResult


def test_single_trusted_case_repeats_in_real_subprocesses():
    result = repeatability.measure(POCRegistry.from_toml(), selected=['POC-G01-03'], repeats=2)
    assert result['repeatability_pass'] is True
    assert result['completed_repeats'] == 2
    assert all(row['statuses'] == {'LOCAL_CHECK_PASS': 1} for row in result['rounds'])
    assert result['full_poc_verification'] == 'NOT_CERTIFIED'


def test_external_never_promoted_to_success():
    result = repeatability.measure(POCRegistry.from_toml(), selected=['POC-G05-06'], repeats=2)
    assert result['repeatability_pass'] is True
    assert all(row['statuses'].get('BLOCKED') for row in result['rounds'])


def test_invalid_repeat_count_fails_closed():
    for count in [0, 11, True, 1.5]:
        with pytest.raises(ValueError):
            repeatability.measure(POCRegistry.from_toml(), repeats=count)


def test_drift_breaks_early(monkeypatch):
    calls = 0
    def fake(self, selected=None, **kwargs):
        nonlocal calls
        calls += 1
        status = 'LOCAL_CHECK_PASS' if calls == 1 else 'TIMEOUT'
        return [RunResult('POC-G01-03', status, 'synthetic')]
    monkeypatch.setattr(repeatability.IsolatedPOCOrchestrator, 'run', fake)
    result = repeatability.measure(POCRegistry.from_toml(), selected=['POC-G01-03'], repeats=4)
    assert not result['repeatability_pass']
    assert result['completed_repeats'] == 2


def test_missing_or_duplicate_rows_rejected(monkeypatch):
    def fake(self, selected=None, **kwargs):
        return [RunResult('POC-G01-03', 'LOCAL_CHECK_PASS', 'synthetic')]*2
    monkeypatch.setattr(repeatability.IsolatedPOCOrchestrator, 'run', fake)
    result = repeatability.measure(POCRegistry.from_toml(), selected=['POC-G01-03'], repeats=2)
    assert not result['repeatability_pass']
    assert result['completed_repeats'] == 1


def test_external_forged_pass_rejected(monkeypatch):
    def fake(self, selected=None, **kwargs):
        return [RunResult('POC-G05-06', 'LOCAL_CHECK_PASS', 'forged')]
    monkeypatch.setattr(repeatability.IsolatedPOCOrchestrator, 'run', fake)
    result = repeatability.measure(POCRegistry.from_toml(), selected=['POC-G05-06'], repeats=2)
    assert not result['repeatability_pass']


def test_too_short_or_large_total_budget_rejected():
    for seconds in [0, 601]:
        with pytest.raises(ValueError):
            repeatability.measure(POCRegistry.from_toml(), selected=['POC-G01-03'], total_timeout_seconds=seconds)
