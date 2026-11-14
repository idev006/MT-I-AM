"""Bounded read-only process-tree resource sampling for trusted POC runs.

Samples are observations, not enforcement or proof of absence of leaks.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import psutil


@dataclass
class TreeTelemetry:
    samples: int = 0
    sample_errors: int = 0
    peak_tree_rss_bytes: int = 0
    peak_process_count: int = 0
    last_process_count: int = 0

    def sample(self, pid: int) -> None:
        try:
            parent = psutil.Process(pid)
            processes = [parent, *parent.children(recursive=True)]
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            self.sample_errors += 1
            return
        rss = 0
        counted = 0
        try:
            for process in processes:
                try:
                    with process.oneshot():
                        rss += process.memory_info().rss
                    counted += 1
                except psutil.NoSuchProcess:
                    continue
        except (psutil.AccessDenied, psutil.ZombieProcess):
            self.sample_errors += 1
            return
        self.samples += 1
        self.peak_tree_rss_bytes = max(self.peak_tree_rss_bytes, rss)
        self.peak_process_count = max(self.peak_process_count, counted)
        self.last_process_count = counted

    def as_report(self) -> dict:
        return {**asdict(self), "measurement_scope": "sampled_parent_and_descendants",
                "complete_census": False}
