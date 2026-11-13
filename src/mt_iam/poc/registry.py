"""Frozen POC identifiers from docs/poc/MASTER_POC_PLAN_v1.0.md.

Descriptions deliberately match the canonical registry. This registry contains PLANS,
not evidence that the POCs have passed. Changes must also update the master plan.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Case:
    id: str
    group: str
    title: str
    priority: str

GROUPS = {
    "G01": ("Runtime & Cloud Infrastructure", "P0", [
        "FastAPI in local OCI and Cloud Run", "Startup, readiness, SIGTERM and shutdown cleanup",
        "Typed config, secret loading and environment isolation",
        "HTTPS, issuer/custom domain and revision routing"]),
    "G02": ("Database & Data Integrity", "P0", [
        "psycopg + SQLAlchemy connection to Supabase PostgreSQL",
        "Alembic schema migrations and controlled recovery path",
        "Transactions, constraints and concurrent atomic writes",
        "Runtime pooler compatibility and prepared statements",
        "Backup/restore to independent PostgreSQL provider"]),
    "G03": ("Modular Architecture & Engine", "P0", [
        "Module boundaries and clean domain ports/adapters",
        "Dependency injection with replaceable fake adapters",
        "Use-case orchestrator coordinating engines",
        "Transactional outbox, idempotency and event contracts",
        "Configuration SSOT, PathManager and engine lifecycle"]),
    "G04": ("Identity & Authentication", "P0", [
        "Identity enrollment and account lifecycle",
        "Password hashing and credential verification policies",
        "MFA, step-up and recovery security flow",
        "Session establishment, expiry and revocation",
        "Suspension/deprovision race conditions"]),
    "G05": ("OIDC / SSO / Federation", "P0", [
        "Evaluate maintained open-source OIDC authorization server",
        "OIDC discovery, JWKS, key custody and rollover",
        "Authorization code + PKCE, state, nonce and validation",
        "Cross-origin two-app SSO with independent permission checks",
        "Logout, revocation and replay/suspension behavior",
        "OIDC conformance and adversarial protocol tests"]),
    "G06": ("Authorization & Governance", "P1", [
        "Actor-role-permission and separation-of-duties matrix",
        "Scoped organization administration",
        "Client app registration/approval and lifecycle",
        "App-local rejection after valid MT-IAM login"]),
    "G07": ("API & Integration", "P1", [
        "OpenAPI-first contracts and compatibility checks",
        "Versioning, errors, pagination and idempotency",
        "Machine API auth, throttling and dependency failure",
        "Cross-language client interoperability and contract checks"]),
    "G08": ("Resource & Concurrency", "P0", [
        "Shared pool ownership and connection cleanup",
        "Structured tasks, cancellation and deadlines",
        "Per-engine concurrency limits, backpressure and bounded queues",
        "Memory/FD/connection stability across repeated workloads",
        "Crash/restart, durable jobs and partial-failure recovery"]),
    "G09": ("Security & Privacy", "P0", [
        "Threat model and risk-selected OWASP ASVS controls",
        "Secrets/key custody, rotation and least privilege",
        "PII minimization, retention, scoped access and audit integrity",
        "Abuse cases: credential attacks, CSRF, replay and privilege escalation"]),
    "G10": ("Automated Testing & Delivery", "P0", [
        "pytest unit/integration/contract harness",
        "Ruff, typing, dependency audit and supply-chain checks",
        "GitHub CI, OCI build, staging deploy and smoke gates",
        "Traceability IDs and automated evidence gates"]),
    "G11": ("Portability & Disaster Recovery", "P1", [
        "Same OCI artifact on Cloud Run and non-Google Linux host",
        "PostgreSQL migration away from Supabase",
        "Issuer/keys/client continuity plus recovery drill"]),
    "G12": ("Operations, Performance & Cost", "P1", [
        "Load, burst, soak and sign-in latency benchmark",
        "Structured telemetry, alerts and incident runbooks",
        "Free-tier attribution, billing review and cost guardrails"]),
}

CASES = tuple(Case(f"POC-{g}-{n:02d}", g, title, priority)
              for g, (_, priority, titles) in GROUPS.items()
              for n, title in enumerate(titles, 1))
BY_ID = {case.id: case for case in CASES}
assert len(CASES) == len(BY_ID) == 52
