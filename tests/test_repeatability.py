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


def test_checkpoint_records_finished_rounds(tmp_path):
    import json
    path = tmp_path / 'checkpoints' / 'run.json'
    result = repeatability.measure(
        POCRegistry.from_toml(), selected=['POC-G01-03'], repeats=2,
        checkpoint_path=path,
    )
    persisted = json.loads(path.read_text())
    assert persisted['stage'] == 'COMPLETE'
    assert persisted['completed_repeats'] == 2
    assert persisted['active_round'] is None
    assert persisted['repeatability_pass'] is True
    assert persisted['full_poc_verification'] == 'NOT_CERTIFIED'
    assert persisted['rounds'] == result['rounds']
    assert not list(path.parent.glob('*.tmp'))


def test_checkpoint_persists_failed_round(tmp_path, monkeypatch):
    import json
    path = tmp_path / 'failed.json'
    def fake(self, selected=None, **kwargs):
        return [RunResult('POC-G01-03', 'TIMEOUT', 'test deadline')]
    monkeypatch.setattr(repeatability.IsolatedPOCOrchestrator, 'run', fake)
    report = repeatability.measure(
        POCRegistry.from_toml(), selected=['POC-G01-03'],
        repeats=3, checkpoint_path=path,
    )
    data = json.loads(path.read_text())
    assert data['stage'] == 'FAILED'
    assert data['completed_repeats'] == 1
    assert not data['repeatability_pass']
    assert report['completed_repeats'] == 1


def test_checkpoint_keeps_running_marker_on_interrupt(tmp_path, monkeypatch):
    import json
    path = tmp_path / 'interrupted.json'
    def interrupted(self, selected=None, **kwargs):
        raise KeyboardInterrupt()
    monkeypatch.setattr(repeatability.IsolatedPOCOrchestrator, 'run', interrupted)
    with pytest.raises(KeyboardInterrupt):
        repeatability.measure(
            POCRegistry.from_toml(), selected=['POC-G01-03'],
            repeats=2, checkpoint_path=path,
        )
    saved = json.loads(path.read_text())
    assert saved['stage'] == 'IN_PROGRESS'
    assert saved['active_round'] == 1
    assert saved['completed_repeats'] == 0
    assert saved['repeatability_pass'] is False
