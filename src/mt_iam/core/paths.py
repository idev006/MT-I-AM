"""Provider-neutral, explicit path management for POC workloads."""

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


@dataclass(frozen=True)
class PathManager:
    """Never assume cwd or a persistent cloud container filesystem."""

    root: Path

    def project_file(self, relative: str) -> Path:
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Path must be relative and must not traverse parents")
        return self.root / path

    @staticmethod
    def scratch() -> TemporaryDirectory[str]:
        """Scoped and automatically cleaned temporary storage."""
        return TemporaryDirectory(prefix="mt-iam-poc-")
