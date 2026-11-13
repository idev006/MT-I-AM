"""Controlled paths and scoped scratch files for disposable POC workloads."""
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

@dataclass(frozen=True)
class PathManager:
    root: Path

    def project_file(self, relative: str) -> Path:
        root = self.root.resolve()
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Path must be relative and must not traverse parents")
        resolved = (root / path).resolve()
        if not resolved.is_relative_to(root):
            raise ValueError("Path escapes configured root")
        return resolved

    @staticmethod
    def scratch() -> TemporaryDirectory[str]:
        return TemporaryDirectory(prefix="mt-iam-poc-")
