"""Verification for isolated runner: real process and bounded scheduler behavior."""
import threading
import time
from pathlib import Path

import pytest

from mt_iam.poc.isolated import IsolatedResult, run_isolated
from mt_iam.poc.platform import IsolatedPOCOrchestrator, POCRegistry, RegistryError
from mt_iam.poc.settings import PlatformSettings


def test_real_trusted_worker_local_check():
    outcome = run_isolated('POC-G01-03', timeout_seconds=10)
    assert outcome.status == 'LOCAL_CHECK_PASS'
    assert 'config' in outcome.detail.lower()


def test_external_or_unknown_handler_fail_closed():
    assert run_isolated('POC-G02-01').status == 'BLOCKED'
    assert run_isolated('POC-G99-99').status == 'BLOCKED'


def test_cancellation_before_spawn():
    event = threading.Event()
    event.set()
    assert run_isolated('POC-G01-03', cancel_event=event).status == 'CANCELLED'


def test_timeout_bounds():
    with pytest.raises(ValueError):
        run_isolated('POC-G01-03', timeout_seconds=0)
    with pytest.raises(ValueError):
        run_isolated('POC-G01-03', timeout_seconds=301)


def test_dry_run_does_not_spawn(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Process should not launch')
    monkeypatch.setattr('mt_iam.poc.platform.run_isolated', forbidden)
    result = IsolatedPOCOrchestrator(POCRegistry.from_toml()).run(
        ['POC-G01-01', 'POC-G05-06'], dry_run=True)
    assert all(x.status == 'NOT_RUN' for x in result)


def test_dependency_blocked_after_fail(monkeypatch, tmp_path):
    registry_override = tmp_path / 'cases.toml'
    registry_override.write_text('''
[[poc]]
id = "POC-G01-02"
depends_on = ["POC-G01-01"]
''')
    def failed(*args, **kwargs):
        return IsolatedResult('TIMEOUT', 'Synthetic timeout')
    monkeypatch.setattr('mt_iam.poc.platform.run_isolated', failed)
    registry = POCRegistry.from_toml(registry_override)
    rows = IsolatedPOCOrchestrator(registry, max_workers=2).run(['POC-G01-02'])
    assert [x.status for x in rows] == ['TIMEOUT', 'BLOCKED']


def test_bounded_workers(monkeypatch):
    active = 0
    peak = 0
    guard = threading.Lock()
    def checking(*args, **kwargs):
        nonlocal active, peak
        with guard:
            active += 1
            peak = max(peak, active)
        time.sleep(0.03)
        with guard:
            active -= 1
        return IsolatedResult('LOCAL_CHECK_PASS', 'local synthetic check')
    monkeypatch.setattr('mt_iam.poc.platform.run_isolated', checking)
    rows = IsolatedPOCOrchestrator(POCRegistry.from_toml(), max_workers=2).run(
        ['POC-G01-01', 'POC-G01-02', 'POC-G01-03', 'POC-G01-04'])
    assert all(x.status == 'LOCAL_CHECK_PASS' for x in rows)
    assert 1 <= peak <= 2


def test_bad_worker_budget_rejected():
    with pytest.raises(RegistryError):
        IsolatedPOCOrchestrator(POCRegistry.from_toml(), max_workers=5)


def test_validated_toml_enables_isolated_mode():
    config = PlatformSettings.load(Path(__file__).resolve().parents[1] / 'configs/platform.toml')
    assert config.orchestrator['execution_mode'] == 'isolated'
    assert config.orchestrator['max_parallel'] == 2


def test_process_cleanup_of_owned_worker():
    """Integration: terminate a synthetic owned subprocess, then reap its PID."""
    import os
    import subprocess
    import sys
    from mt_iam.poc.isolated import _terminate_tree

    process = subprocess.Popen(
        [sys.executable, '-c', 'import time; time.sleep(15)'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        start_new_session=(os.name != 'nt'),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
    )
    _terminate_tree(process)
    assert process.poll() is not None


def test_full_registry_isolated_run_preserves_non_certification():
    """Execute actual worker processes and keep external blockers explicit."""
    from mt_iam.poc.platform import report
    from collections import Counter

    outputs = IsolatedPOCOrchestrator(POCRegistry.from_toml(), max_workers=2,
                                      timeout_seconds=15).run()
    counts = Counter(row.status for row in outputs)
    assert len(outputs) == 52
    assert counts['LOCAL_CHECK_PASS'] == 30
    assert counts['BLOCKED'] == 22
    assert report(outputs)['full_poc_verification'] == 'NOT_CERTIFIED'
