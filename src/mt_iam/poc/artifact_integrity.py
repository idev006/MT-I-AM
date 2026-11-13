"""Bounded, read-only verification of evidence files under an approved root.

Digest checks do not authenticate a reviewer or certify production readiness.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
from pathlib import Path
import re
import stat
from typing import Any

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
MAX_ARTIFACTS = 32
MAX_ARTIFACT_BYTES = 16 * 1024 * 1024


@dataclass(frozen=True)
class ArtifactAudit:
    verified: bool
    errors: tuple[str, ...]
    files_checked: int


def verify_artifacts(manifest: dict[str, Any], root: Path) -> ArtifactAudit:
    """Check regular-file digests without allowing traversal, symlinks or devices."""
    errors: list[str] = []
    checked = 0
    entries = manifest.get("artifacts") if isinstance(manifest, dict) else None
    if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_ARTIFACTS:
        return ArtifactAudit(False, ("Artifact count outside permitted range",), 0)
    root = Path(root).absolute()
    if root.is_symlink() or not root.is_dir():
        return ArtifactAudit(False, ("Artifact root must be an existing non-symlink directory",), 0)
    root = root.resolve(strict=True)
    seen: set[str] = set()
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"Artifact #{i}: entry must be an object")
            continue
        relative = entry.get("path")
        digest = entry.get("sha256")
        if not isinstance(relative, str) or not relative or "\\" in relative:
            errors.append(f"Artifact #{i}: invalid relative path")
            continue
        path = Path(relative)
        if path.is_absolute() or any(part in ("..", ".") for part in relative.split("/")) or ":" in relative:
            errors.append(f"Artifact #{i}: unsafe path")
            continue
        if relative in seen:
            errors.append(f"Artifact #{i}: duplicate path")
            continue
        seen.add(relative)
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            errors.append(f"Artifact #{i}: invalid SHA-256")
            continue
        candidate = root / path
        try:
            current = root
            for part in path.parts:
                current = current / part
                if current.is_symlink():
                    raise ValueError("symlink forbidden")
            resolved = candidate.resolve(strict=True)
            if not resolved.is_relative_to(root):
                raise ValueError("path outside root")
            info = resolved.stat()
            if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_ARTIFACT_BYTES:
                raise ValueError("not a regular bounded file")
            sha = hashlib.sha256()
            with resolved.open("rb") as stream:
                remaining = MAX_ARTIFACT_BYTES + 1
                while chunk := stream.read(min(65536, remaining)):
                    remaining -= len(chunk)
                    if remaining < 0:
                        raise ValueError("artifact exceeded size bound")
                    sha.update(chunk)
            if not hmac.compare_digest(sha.hexdigest(), digest):
                raise ValueError("SHA-256 mismatch")
            checked += 1
        except (OSError, ValueError):
            errors.append(f"Artifact #{i}: unavailable, unsafe or digest mismatch")
    return ArtifactAudit(not errors and checked == len(entries), tuple(errors), checked)
