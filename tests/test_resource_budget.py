"""Run bounded-worker resource-limit checks without cloud credentials."""
import os
import subprocess
import sys

import pytest

from mt_iam.poc.resource_budget import WorkerBudget
from mt_iam.poc.settings import PlatformSettings
from mt_iam.poc.isolated import run_isolated
from mt_iam.poc.platform import RegistryError


@pytest.mark.parametrize('memory,cpu', [(0, 1), (127, 1), (4097, 1), (768, 0), (768, 301), (True, 10)])
def test_budget_rejects_bad_limits(memory, cpu):
    with pytest.raises(ValueError):
        WorkerBudget(memory, cpu)


def test_runner_under_bounded_posix_budget():
    if os.name == 'nt':
        pytest.skip('Windows job limits require Windows integration')
    r = run_isolated('POC-G01-03', timeout_seconds=5, budget=WorkerBudget(512, 5))
    assert r.status == 'LOCAL_CHECK_PASS'


def test_toml_budget_roundtrip(tmp_path):
    config = tmp_path / 'platform.toml'
    config.write_text('[poc.orchestrator]\nexecution_mode="isolated"\n[poc.resources]\nmemory_mb=512\ncpu_seconds=5\n')
    result = PlatformSettings.load(config)
    assert result.resources == {'memory_mb': 512, 'cpu_seconds': 5}


def test_toml_budget_rejects_oversized(tmp_path):
    config = tmp_path / 'platform.toml'
    config.write_text('[poc.resources]\nmemory_mb=100000\ncpu_seconds=5\n')
    with pytest.raises(RegistryError):
        PlatformSettings.load(config)


@pytest.mark.skipif(os.name == 'nt', reason='POSIX-only resource limits')
def test_posix_worker_enforces_cpu_seconds():
    script = '''from mt_iam.poc.resource_budget import WorkerBudget,enforce_posix_budget
import signal
signal.signal(signal.SIGXCPU, lambda *_: exit(73))
enforce_posix_budget(WorkerBudget(512,1))
while True: pass
'''
    result = subprocess.run([sys.executable, '-c', script], capture_output=True, timeout=8)
    assert result.returncode != 0


@pytest.mark.skipif(os.name == 'nt', reason='POSIX-only resource limits')
def test_posix_worker_memory_bound():
    script = '''from mt_iam.poc.resource_budget import WorkerBudget,enforce_posix_budget
import sys
try:
    enforce_posix_budget(WorkerBudget(128,5))
    b = bytearray(512 * 1024 * 1024)
except MemoryError:
    sys.exit(74)
else:
    sys.exit(0)
'''
    result = subprocess.run([sys.executable, '-c', script], capture_output=True, timeout=6)
    assert result.returncode != 0


@pytest.mark.skipif(os.name != 'nt', reason='Windows-only Job Object memory limit')
def test_windows_job_memory_budget_is_enforced():
    script = '''from mt_iam.poc.windows_job import managed_worker_lifetime
from mt_iam.poc.resource_budget import WorkerBudget
with managed_worker_lifetime(WorkerBudget(128, 10)):
    try:
        _data = bytearray(512 * 1024 * 1024)
    except MemoryError:
        raise SystemExit(74)
    raise SystemExit(0)
'''
    result = subprocess.run([sys.executable, '-c', script], timeout=15, capture_output=True)
    assert result.returncode != 0


@pytest.mark.skipif(os.name != 'nt', reason='Windows-only Job Object CPU limit')
def test_windows_job_cpu_budget_is_enforced():
    script = '''from mt_iam.poc.windows_job import managed_worker_lifetime
from mt_iam.poc.resource_budget import WorkerBudget
with managed_worker_lifetime(WorkerBudget(512, 1)):
    while True: pass
'''
    result = subprocess.run([sys.executable, '-c', script], timeout=10, capture_output=True)
    assert result.returncode != 0
