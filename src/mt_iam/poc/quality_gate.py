"""POC evidence completeness gate: never promote local diagnostics into full verification."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import argparse
import json
import re

from mt_iam.poc.platform import POCRegistry
from mt_iam.poc.artifact_integrity import verify_artifacts

SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_RESULTS = {"PASS", "FAIL", "BLOCKED", "NOT_RUN"}


@dataclass(frozen=True)
class GateResult:
    accepted: bool
    problems: tuple[str, ...]


def check_evidence(document: dict[str, Any], registry: POCRegistry) -> GateResult:
    """Check evidence manifest structure, NOT the real-world authenticity of artifacts."""
    problems: list[str] = []
    if not isinstance(document, dict):
        return GateResult(False, ("Evidence must be an object",))
    poc_id = document.get("poc_id")
    if not isinstance(poc_id, str) or poc_id not in registry.by_id:
        return GateResult(False, ("Unknown POC ID",))
    if document.get("schema_version") != 1:
        problems.append("Unsupported evidence schema")
    status = document.get("verification_status")
    if status not in ALLOWED_RESULTS:
        problems.append("Verification must use PASS/FAIL/BLOCKED/NOT_RUN")
    if document.get("runner_status") == "LOCAL_CHECK_PASS" and status == "PASS":
        if not document.get("external_or_scope_evidence"):
            problems.append("Local check is insufficient for full POC PASS")
    if status == "PASS":
        if not isinstance(document.get("source_sha"), str) or not SHA.fullmatch(document["source_sha"]):
            problems.append("Full source commit SHA required")
        if not isinstance(document.get("environment"), str) or len(document["environment"].strip()) < 5:
            problems.append("Environment description required")
        if not isinstance(document.get("command"), str) or not document["command"].strip():
            problems.append("Reproducible test command required")
        cases = document.get("cases")
        if not isinstance(cases, list) or len(cases) < 2:
            problems.append("At least two scoped test cases are required")
        else:
            kinds = set()
            for case in cases:
                if not isinstance(case, dict) or case.get("status") != "PASS" or case.get("kind") not in ("positive", "negative", "failure", "resource", "integration"):
                    problems.append("Test cases must all have PASS and approved kind")
                    break
                kinds.add(case["kind"])
            if not {"positive", "negative"}.issubset(kinds):
                problems.append("Positive and negative test coverage required")
        evidence = document.get("artifacts")
        if not isinstance(evidence, list) or not evidence:
            problems.append("At least one evidence artifact and hash required")
        else:
            for artifact in evidence:
                if not isinstance(artifact, dict) or not isinstance(artifact.get("sha256"), str) or not DIGEST.fullmatch(artifact["sha256"]):
                    problems.append("Evidence artifact SHA-256 required")
                    break
        reviewer = document.get("reviewer")
        author = document.get("owner")
        if not isinstance(author, str) or not author.strip() or not isinstance(reviewer, str) or not reviewer.strip() or author == reviewer:
            problems.append("Independent owner and reviewer required")
        if document.get("review_decision") != "ACCEPT":
            problems.append("Explicit independent review acceptance required")
        if document.get("resource_cleanup") != "VERIFIED":
            problems.append("Resource cleanup verification required")
        if registry.by_id[poc_id].mode == "external" and document.get("external_or_scope_evidence") != "VERIFIED":
            problems.append("External POC requires verified provider/standard evidence")
    return GateResult(not problems and status == "PASS", tuple(problems or ([f"Result is {status}, not PASS"] if status != "PASS" else [])))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check independent POC acceptance evidence")
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--artifact-root", type=Path, default=None,
                        help="Required for CLI PASS: validate actual local evidence file digests")
    args = parser.parse_args(argv)
    try:
        if args.evidence.stat().st_size > 1024 * 1024:
            raise ValueError("Evidence exceeds 1 MiB")
        payload = json.loads(args.evidence.read_text(encoding="utf-8"))
        gate = check_evidence(payload, POCRegistry.from_toml(args.registry))
        if gate.accepted:
            if args.artifact_root is None:
                print('BLOCKED: --artifact-root required to validate evidence bytes')
                return 2
            audit = verify_artifacts(payload, args.artifact_root)
            if not audit.verified:
                print('BLOCKED: ' + '; '.join(audit.errors))
                return 2
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"BLOCKED: Cannot validate evidence ({type(exc).__name__})")
        return 2
    print("PASS: Evidence completeness gate" if gate.accepted else "BLOCKED: " + "; ".join(gate.problems))
    return 0 if gate.accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
