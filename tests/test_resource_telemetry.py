"""Test representative process-tree peak observation and supervisor persistence."""
import json
import subprocess
import sys
import time

from mt_iam.poc.resource_telemetry import TreeTelemetry
from mt_iam.poc.repeatability_supervisor import _supervise_command


def test_live_process_tree_memory_observation():
    program = 'import time; block=bytearray(20*1024*1024);time.sleep(2)'
    worker = subprocess.Popen([sys.executable, '-c', program])
    try:
        sampler = TreeTelemetry()
        deadline = time.monotonic() + 1.5
        while time.monotonic() < deadline:
            sampler.sample(worker.pid)
            if sampler.peak_tree_rss_bytes >= 20 * 1024 * 1024:
                break
            time.sleep(.05)
        assert sampler.samples >= 1
        assert sampler.peak_process_count >= 1
        assert sampler.peak_tree_rss_bytes >= 20 * 1024 * 1024
        report = sampler.as_report()
        assert report['complete_census'] is False
    finally:
        worker.kill()
        worker.wait()


def test_supervisor_writes_telemetry_on_timeout(tmp_path):
    report = tmp_path / 'timeout.json'
    rc = _supervise_command([sys.executable, '-c', 'import time;time.sleep(30)'],
                            report=report, hard_timeout_seconds=.4)
    payload = json.loads(report.read_text())
    assert rc == 124
    assert payload['resource_telemetry']['samples'] >= 1
    assert payload['resource_telemetry']['peak_process_count'] >= 1
    assert payload['repeatability_pass'] is False


def test_supervisor_writes_telemetry_on_failure(tmp_path):
    report = tmp_path / 'failed.json'
    rc = _supervise_command([sys.executable, '-c', 'pass'],
                            report=report, hard_timeout_seconds=3)
    payload = json.loads(report.read_text())
    assert rc == 1
    assert 'resource_telemetry' in payload
