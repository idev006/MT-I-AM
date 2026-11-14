"""Real subprocess, deadline, and checkpoint preservation regression tests."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time

import pytest
from mt_iam.poc.repeatability_supervisor import _supervise_command


def test_real_small_local_repeatability(tmp_path):
    report = tmp_path / "small.json"
    command = [sys.executable, "-m", "mt_iam.poc.repeatability", "--id", "POC-G01-03",
               "--repeats", "2", "--report", str(report)]
    code = _supervise_command(command, report=report, hard_timeout_seconds=20)
    data = json.loads(report.read_text())
    assert code == 0 and data["stage"] == "COMPLETE"
    assert data["completed_repeats"] == 2
    assert data["full_poc_verification"] == "NOT_CERTIFIED"


def test_hard_timeout_preserves_partial_results(tmp_path):
    report = tmp_path / "timeout.json"
    program = ("import json,time,sys;"
               "open(sys.argv[1],'w').write(json.dumps({'schema_version':2,"
               "'stage':'IN_PROGRESS','completed_repeats':1,'rounds':[{'run':1}],"
               "'full_poc_verification':'NOT_CERTIFIED','repeatability_pass':False}));"
               "time.sleep(30)")
    code = _supervise_command([sys.executable, "-c", program, str(report)],
                              report=report, hard_timeout_seconds=0.7)
    data = json.loads(report.read_text())
    assert code == 124 and data["stage"] == "TIMEOUT"
    assert data["completed_repeats"] == 1
    assert data["rounds"] == [{"run": 1}]
    assert not data["repeatability_pass"]


def test_does_not_overwrite_old_evidence(tmp_path):
    report = tmp_path / "existing.json"
    report.write_text("historical")
    with pytest.raises(FileExistsError):
        _supervise_command([sys.executable, "-c", "pass"],
                           report=report, hard_timeout_seconds=2)
    assert report.read_text() == "historical"


def test_success_without_completed_report_is_failure(tmp_path):
    report = tmp_path / "missing.json"
    code = _supervise_command([sys.executable, "-c", "pass"],
                              report=report, hard_timeout_seconds=2)
    data = json.loads(report.read_text())
    assert code == 1 and data["stage"] == "FAILED"


@pytest.mark.skipif(os.name == "nt", reason="POSIX process-group probe")
def test_deadline_kills_descendants(tmp_path):
    report = tmp_path / "tree.json"
    pidfile = tmp_path / "child.pid"
    program = ("import subprocess,sys,time;"
               "p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'],"
               "stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);"
               "open(sys.argv[1],'w').write(str(p.pid));time.sleep(30)")
    code = _supervise_command([sys.executable, "-c", program, str(pidfile)],
                              report=report, hard_timeout_seconds=1)
    assert code == 124 and pidfile.exists()
    procstat = Path(f"/proc/{int(pidfile.read_text())}/stat")
    deadline = time.monotonic() + 2
    while procstat.exists() and time.monotonic() < deadline:
        if procstat.read_text().split()[2] == "Z":
            break
        time.sleep(0.025)
    if procstat.exists():
        assert procstat.read_text().split()[2] == "Z"
