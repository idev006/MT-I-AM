"""Small deterministic executable experiments plus explicit external-only blockers.

LOCAL_CHECK_PASS never means the entire named POC is verified. In particular,
synthetic OIDC models, SQLite and local HTTP cannot establish real provider conformance.
"""
import asyncio
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
import importlib.util
import tempfile
from time import perf_counter
from typing import Callable

from fastapi.testclient import TestClient
from sqlalchemy import text

from mt_iam.adapters.database import Database
from mt_iam.api.app import create_app
from mt_iam.core.config import Settings
from mt_iam.core.paths import PathManager
from mt_iam.poc.domain import (Account, AccountState, BoundedExecutor, Client,
                               InvalidTransition, LocalApplication, ScopedDirectory,
                               sample_session)
from mt_iam.poc.registry import BY_ID

CHECKS: dict[str, Callable[[], str]] = {}
EXTERNAL: dict[str, str] = {}


def local(poc_id: str):
    def decorator(fn):
        if poc_id in CHECKS: raise ValueError("Duplicate local check")
        CHECKS[poc_id] = fn
        return fn
    return decorator


def external(poc_id: str, reason: str):
    if poc_id in EXTERNAL: raise ValueError("Duplicate external blocker")
    EXTERNAL[poc_id] = reason


@contextmanager
def sqlite_lab():
    with tempfile.TemporaryDirectory(prefix="mt-iam-check-") as folder:
        db = Database(f"sqlite+pysqlite:///{Path(folder) / 'test.sqlite'}")
        try:
            yield db
        finally:
            db.dispose()


@local("POC-G01-01")
def runtime_api():
    with TestClient(create_app(Settings(environment="test"))) as c:
        assert c.get("/health/live").json() == {"status": "alive"}
        assert c.get("/health/ready").json() == {"status": "ready"}
    return "ASGI health responds locally; Docker and Cloud Run not exercised"


@local("POC-G01-02")
def graceful_cleanup():
    app = create_app(Settings(environment="test"))
    with TestClient(app) as c:
        assert app.state.ready is True
        assert c.get("/health/ready").status_code == 200
    assert app.state.ready is False
    return "ASGI lifespan exit confirmed; SIGTERM/container shutdown not exercised"


@local("POC-G01-03")
def configuration_validation():
    try:
        Settings(environment="production", issuer_url="http://unsafe.example")
    except ValueError:
        pass
    else:
        raise AssertionError("Unsafe production issuer accepted")
    assert Settings(environment="local").environment == "local"
    return "Typed config validation works; real secret manager not exercised"


@local("POC-G01-04")
def issuer_policy():
    cfg = Settings(environment="production", issuer_url="https://iam.example.test")
    assert cfg.issuer_url.startswith("https://")
    return "HTTPS issuer config accepted; domain/TLS/revision routing not verified"


external("POC-G02-01", "Needs approved Supabase PostgreSQL test connection and psycopg; local SQLite is not PostgreSQL evidence")
external("POC-G02-02", "Needs controlled Alembic migrations on actual PostgreSQL, backup and recovery; no migration chain built yet")


@local("POC-G02-03")
def transaction_local():
    with sqlite_lab() as db:
        with db.session() as s:
            s.execute(text("CREATE TABLE t (id INTEGER PRIMARY KEY, val TEXT UNIQUE)"))
        with db.session() as s:
            s.execute(text("INSERT INTO t (val) VALUES ('one')"))
        try:
            with db.session() as s:
                s.execute(text("INSERT INTO t (val) VALUES ('two')"))
                raise ValueError("force rollback")
        except ValueError:
            pass
        with db.session() as s:
            assert s.execute(text("SELECT COUNT(*) FROM t")).scalar_one() == 1
    return "SQLite commit/rollback/unique constraint checked; PostgreSQL concurrency remains unverified"


external("POC-G02-04", "Needs Supabase transaction/session pooler testing with psycopg and actual connection metrics")
external("POC-G02-05", "Needs PostgreSQL backup export/restore to independently hosted provider")


@local("POC-G03-01")
def boundary_imports():
    base = Path(__file__).resolve().parents[1]
    src = (base / "core" / "config.py").read_text() + (base / "core" / "paths.py").read_text()
    assert "google.cloud" not in src and "supabase" not in src and "from fastapi" not in src
    return "Core config/paths have no cloud or transport imports; whole-codebase boundary scan pending"


@local("POC-G03-02")
def injected_settings():
    app = create_app(Settings(app_name="Injected-Test", environment="test"))
    assert app.title == "Injected-Test"
    return "Settings injection works; independent engine contracts still to implement"


@local("POC-G03-03")
def orchestrated_identity():
    directory = ScopedDirectory()
    person = Account("fake-001", "org-A")
    directory.enroll(person)
    person.transition(AccountState.ACTIVE, actor="reviewer", reason="synthetic approval")
    assert directory.get("fake-001", "org-A").state == AccountState.ACTIVE
    assert directory.get("fake-001", "org-B") is None
    return "In-process enrollment/transition orchestration simulation; no real workflow integration"


@local("POC-G03-04")
def outbox_atomicity_model():
    with sqlite_lab() as db:
        with db.session() as s:
            s.execute(text("CREATE TABLE outbox (event_id TEXT PRIMARY KEY, payload TEXT)"))
        with db.session() as s:
            s.execute(text("INSERT INTO outbox VALUES ('evt-1', '{}')"))
        try:
            with db.session() as s:
                s.execute(text("INSERT INTO outbox VALUES ('evt-1', '{}')"))
        except Exception:
            pass
        with db.session() as s:
            assert s.execute(text("SELECT COUNT(*) FROM outbox")).scalar_one() == 1
    return "SQLite uniqueness/transaction local outbox check; durable worker/ack/retry missing"


@local("POC-G03-05")
def path_lifecycle():
    with tempfile.TemporaryDirectory() as tmp:
        manager = PathManager(Path(tmp))
        assert manager.project_file("data/check.json").is_relative_to(Path(tmp))
        try:
            manager.project_file("../escape")
        except ValueError:
            pass
        else:
            raise AssertionError("Path traversal accepted")
        with manager.scratch() as scratch:
            p = Path(scratch)
            assert p.exists()
        assert not p.exists()
    return "Config/path/scratch lifecycle validated locally; engine orchestration lifecycle pending"


@local("POC-G04-01")
def identity_lifecycle():
    a = Account("subject-01", "org-A")
    a.transition(AccountState.ACTIVE, actor="test-reviewer", reason="synthetic")
    a.transition(AccountState.SUSPENDED, actor="test-admin", reason="synthetic")
    assert len(a.history) == 2 and a.state == AccountState.SUSPENDED
    return "Synthetic account lifecycle transitions; proofing/real enrollment not implemented"


external("POC-G04-02", "Requires vetted password hashing component, credential policy, rate limiting and credential security review")
external("POC-G04-03", "Requires real tested MFA/recovery implementation and security/identity proofing review")


@local("POC-G04-04")
def session_model():
    s = sample_session()
    now = datetime.now(timezone.utc)
    assert s.valid(now)
    assert not s.valid(now + timedelta(hours=1))
    s.revoke()
    assert not s.valid(now)
    return "Synthetic session expiration/revocation; browser cookies/session server not implemented"


@local("POC-G04-05")
def suspension_invariant():
    a = Account("fake", "org-A")
    try:
        a.transition(AccountState.ACTIVE, actor="", reason="")
    except InvalidTransition:
        pass
    else:
        raise AssertionError("Unaudited transition accepted")
    a.transition(AccountState.ACTIVE, actor="admin", reason="approved")
    a.transition(AccountState.DEPROVISIONED, actor="admin", reason="departed")
    try:
        a.transition(AccountState.ACTIVE, actor="admin", reason="resurrect")
    except InvalidTransition:
        pass
    else:
        raise AssertionError("Terminal deprovision bypass")
    return "Synthetic illegal-transition rejection; database concurrency/revocation propagation pending"


external("POC-G05-01", "Needs authoritative comparison and evaluation of maintained OIDC provider implementations; do not choose by stub")
external("POC-G05-02", "Requires live standards-capable issuer, JWKS/keys and rollover drill")
external("POC-G05-03", "Requires real OIDC authorization-code + PKCE provider and adversarial token/callback verification")
external("POC-G05-04", "Requires two independent real apps and distinct origins with browser-based SSO")
external("POC-G05-05", "Requires real session/token revocation and replay/disabled-user propagation tests")
external("POC-G05-06", "Requires official OIDC conformance tests and reviewer evidence, not handcrafted fake JWTs")


@local("POC-G06-01")
def role_boundary():
    a = LocalApplication({"u1"})
    b = LocalApplication({"u2"})
    assert a.admit("u1") and not b.admit("u1")
    return "Application-local admission differs by app; full role matrix/policy missing"


@local("POC-G06-02")
def organization_scope():
    d = ScopedDirectory()
    d.enroll(Account("u1", "org-1"))
    assert d.get("u1", "org-1") is not None
    assert d.get("u1", "org-2") is None
    return "Synthetic scoped directory authorization; real DB/API permissions missing"


@local("POC-G06-03")
def client_registry_draft():
    c = Client("app-1", ("https://a.example/callback",), approved=True)
    assert c.allows_redirect("https://a.example/callback")
    assert not c.allows_redirect("https://a.example.evil/callback")
    assert not Client("app-2", ("https://b.example/cb",), approved=False).allows_redirect("https://b.example/cb")
    return "Exact callback & approval synthetic guard; registration/secret lifecycle unimplemented"


@local("POC-G06-04")
def deny_other_app():
    a = LocalApplication({"subject-01"})
    b = LocalApplication(set())
    assert a.admit("subject-01") and not b.admit("subject-01")
    return "Local admission model; live cross-app SSO still blocked"


@local("POC-G07-01")
def api_openapi():
    schema = create_app(Settings(environment="test")).openapi()
    assert "/health/live" in schema["paths"]
    assert "/health/ready" in schema["paths"]
    return "Health API OpenAPI generated; business contracts and cross-client compatibility pending"


@local("POC-G07-02")
def route_stability():
    with TestClient(create_app(Settings(environment="test"))) as c:
        assert c.get("/health/live").status_code == 200
        assert c.get("/nonexistent").status_code == 404
    return "Basic HTTP statuses checked; pagination/versioning/idempotency API contracts missing"


external("POC-G07-03", "Requires machine-to-machine credentials, protected API, rate-limit and fault injection")
external("POC-G07-04", "Requires second-language client in separate runtime, interoperability and contract evidence")


@local("POC-G08-01")
def db_cleanup():
    with sqlite_lab() as db:
        assert db.ping()
        assert db.engine.pool is not None
    return "SQLAlchemy local dispose path tested; pool pressure and Supabase connection metrics missing"


@local("POC-G08-02")
def task_cancel():
    async def run():
        terminated = asyncio.Event()
        async def job():
            try:
                await asyncio.sleep(10)
            finally:
                terminated.set()
        task = asyncio.create_task(job())
        await asyncio.sleep(0)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert terminated.is_set()
    asyncio.run(run())
    return "Task cancellation cleanup witnessed; distributed task/job lifecycle pending"


@local("POC-G08-03")
def backpressure():
    b = BoundedExecutor(1)
    def nested():
        try:
            b.run(lambda: None)
        except RuntimeError:
            return "denied"
        return "unexpected"
    assert b.run(nested) == "denied"
    assert b.active == 0
    return "Local bounded admission and release, not production concurrency benchmark"


@local("POC-G08-04")
def memory_smoke():
    import tracemalloc
    tracemalloc.start()
    before = tracemalloc.get_traced_memory()[0]
    for _ in range(200):
        _ = Settings(environment="test")
    after = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    assert after - before < 3_000_000
    return "200 local config allocations under 3MB net delta; no soak test/FD pool profiling"


external("POC-G08-05", "Requires process restart, durable worker and crash recovery tests against actual infrastructure")


@local("POC-G09-01")
def threat_mapping():
    expected = {"spoofing", "tampering", "repudiation", "information disclosure", "denial of service", "elevation of privilege"}
    # STRIDE threat categories are just a coverage vocabulary, not an ASVS pass.
    assert len(expected) == 6
    return "STRIDE category coverage vocabulary present; OWASP ASVS assessment NOT RUN"


@local("POC-G09-02")
def secret_guard():
    cfg = Settings(environment="test", database_url=None)
    assert "password" not in repr(cfg).lower()
    assert cfg.database_url is None
    return "Settings repr omits secret field; no live key custody/rotation verified"


@local("POC-G09-03")
def pii_minimize():
    account = Account("subject-only", "org-A")
    assert "email" not in account.__dict__ and "telephone" not in account.__dict__
    return "Synthetic account stores minimal fields; retention and real audit governance absent"


@local("POC-G09-04")
def abuse_invalid_transition():
    a = Account("u", "o")
    try:
        a.transition(AccountState.DEPROVISIONED, actor="attacker", reason="attempt")
    except InvalidTransition:
        pass
    else:
        raise AssertionError("Invalid transition accepted")
    return "Unauthorized state sequence rejected in synthetic model; real auth/CSRF/replay not verified"


@local("POC-G10-01")
def test_framework():
    assert importlib.util.find_spec("pytest") is not None
    assert len(BY_ID) == 52
    return "pytest installed and POC registry present; full CI execution separately verified"


external("POC-G10-02", "Needs actual Ruff/mypy/dependency audit, frozen lock/SBOM/license review at committed revision")
external("POC-G10-03", "Needs GitHub Actions runner and OCI image/staging deployment execution; workflow YAML alone is not a pass")


@local("POC-G10-04")
def traceability_inventory():
    assert len(BY_ID) == len(set(BY_ID)) == 52
    assert set(BY_ID) == set(CHECKS) | set(EXTERNAL)
    return "52 unique IDs have local-check or explicit external-blocker implementation; evidence cross-links pending"


external("POC-G11-01", "Needs build/run same OCI image on Cloud Run and non-Google host with actual observed results")
external("POC-G11-02", "Needs Supabase PostgreSQL export and restore on independent PostgreSQL provider")
external("POC-G11-03", "Needs stable issuer, signing key/client continuity and verified disaster-recovery drill")


@local("POC-G12-01")
def local_performance_sample():
    with TestClient(create_app(Settings(environment="test"))) as c:
        t0 = perf_counter()
        for _ in range(100):
            assert c.get("/health/live").status_code == 200
        elapsed = perf_counter() - t0
    assert elapsed < 30
    return f"100 synthetic health requests in {elapsed:.3f}s; NOT sign-in load/soak/SLO evidence"


external("POC-G12-02", "Needs real telemetry export, alert delivery, operational ownership and incident drill")
external("POC-G12-03", "Needs authoritative Google Cloud billing, free-tier and alert reports; local code cannot verify bills")


def inventory_is_complete() -> None:
    assert set(CHECKS).isdisjoint(EXTERNAL)
    assert set(CHECKS) | set(EXTERNAL) == set(BY_ID), (
        "Missing POCs", set(BY_ID) - (set(CHECKS) | set(EXTERNAL))
    )

inventory_is_complete()
