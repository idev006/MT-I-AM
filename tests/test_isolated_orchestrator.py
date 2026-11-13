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


def test_worker_env_excludes_sensitive_tokens(monkeypatch):
    from mt_iam.poc.isolated import _safe_worker_env
    monkeypatch.setenv("MT_IAM_DATABASE_URL", "postgresql://private")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "private")
    monkeypatch.setenv("PYTHONIOENCODING", "utf-8")
    env = _safe_worker_env()
    assert "MT_IAM_DATABASE_URL" not in env
    assert "AWS_SECRET_ACCESS_KEY" not in env
    assert env["PYTHONIOENCODING"] == "utf-8"


def test_cancel_started_process(monkeypatch):
    import subprocess
    import sys
    from mt_iam.poc import isolated
    original = subprocess.Popen

    def sleeper(_args, **kwargs):
        return original([sys.executable, "-c", "import time; time.sleep(10)"], **kwargs)

    monkeypatch.setattr(isolated, "_spawn_worker", sleeper)
    event = threading.Event()
    timer = threading.Timer(0.15, event.set)
    timer.start()
    try:
        start = time.monotonic()
        result = isolated.run_isolated("POC-G01-03", timeout_seconds=3, cancel_event=event)
        assert result.status == "CANCELLED"
        assert time.monotonic() - start < 3
    finally:
        timer.join()


def test_timeout_terminates_started_process(monkeypatch):
    import subprocess
    import sys
    from mt_iam.poc import isolated
    original = subprocess.Popen

    def sleeper(_args, **kwargs):
        return original([sys.executable, "-c", "import time; time.sleep(10)"], **kwargs)

    monkeypatch.setattr(isolated, "_spawn_worker", sleeper)
    start = time.monotonic()
    result = isolated.run_isolated("POC-G01-03", timeout_seconds=0.2)
    assert result.status == "TIMEOUT"
    assert time.monotonic() - start < 3


def test_worker_output_capped_on_disk(monkeypatch):
    import subprocess
    import sys
    from mt_iam.poc import isolated
    original = subprocess.Popen

    def noisy(_args, **kwargs):
        return original([sys.executable, "-c", 'import sys; sys.stdout.write("X" * 80000)'], **kwargs)

    monkeypatch.setattr(isolated, "_spawn_worker", noisy)
    result = isolated.run_isolated("POC-G01-03", timeout_seconds=5)
    assert result.status == "FAIL"
    assert "output exceeded" in result.detail


def test_report_counts_timeout_and_cancellation():
    from mt_iam.poc.platform import RunResult, report
    result = report([RunResult("POC-G01-01", "TIMEOUT", "timeout"),
                     RunResult("POC-G01-02", "CANCELLED", "cancelled")])
    assert result["summary"]["TIMEOUT"] == 1
    assert result["summary"]["CANCELLED"] == 1
    assert result["full_poc_verification"] == "NOT_CERTIFIED"

@pytest.mark.skipif(__import__('os').name == 'nt', reason='POSIX process group test')
def test_successful_worker_still_cleans_descendants(monkeypatch, tmp_path):
    """A worker can exit 0 while leaving a child in its process group."""
    import os
    import subprocess
    import sys
    from mt_iam.poc import isolated

    child_pid = tmp_path / 'child.pid'
    script = (
        'import subprocess,sys,json;'
        'p=subprocess.Popen([sys.executable,"-c","import time;time.sleep(30)"],'
        'stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);'
        f'open({str(child_pid)!r},"w").write(str(p.pid));'
        'print(json.dumps({"status":"LOCAL_CHECK_PASS","detail":"synthetic"}),flush=True)'
    )
    original = subprocess.Popen

    def worker(_args, **kwargs):
        return original([sys.executable, '-c', script], **kwargs)

    monkeypatch.setattr(isolated, '_spawn_worker', worker)
    try:
        outcome = isolated.run_isolated('POC-G01-03', timeout_seconds=5)
        assert outcome.status == 'LOCAL_CHECK_PASS'
        assert child_pid.exists()
        pid = int(child_pid.read_text())
        # A killed descendant may briefly remain a zombie while being reaped.
        proc_stat = Path(f'/proc/{pid}/stat')
        deadline = time.monotonic() + 2
        while proc_stat.exists() and time.monotonic() < deadline:
            if proc_stat.read_text().split()[2] == 'Z':
                break
            time.sleep(0.025)
        if proc_stat.exists():
            assert proc_stat.read_text().split()[2] == 'Z'
    finally:
        if child_pid.exists():
            import signal
            try:
                os.kill(int(child_pid.read_text()), signal.SIGKILL)
            except ProcessLookupError:
                pass
