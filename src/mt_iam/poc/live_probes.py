"""Explicit, opt-in, read-only live probes. Never prints credentials or token bodies.

A successful probe is LIVE_PARTIAL, never entire-P0C PASS or OIDC conformance.
No connection or cloud API use happens without opt-in and environment configuration.
"""
import argparse
import os
import sys
from urllib.parse import urlsplit

import httpx


def require_https(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Only HTTPS URLs without embedded credentials are permitted")
    if parsed.fragment:
        raise ValueError("Fragments forbidden")
    return url.rstrip("/")


def probe_cloudrun_health(url: str) -> str:
    endpoint = require_https(url) + "/health/live"
    with httpx.Client(timeout=5.0, follow_redirects=False) as client:
        response = client.get(endpoint)
        response.raise_for_status()
        if response.json().get("status") != "alive":
            raise ValueError("Unexpected health response")
    return "LIVE_PARTIAL: HTTPS health endpoint responded; no shutdown/scale/cost verification"


def probe_oidc_discovery(issuer: str) -> str:
    issuer = require_https(issuer)
    with httpx.Client(timeout=5.0, follow_redirects=False) as client:
        response = client.get(issuer + "/.well-known/openid-configuration")
        response.raise_for_status()
        obj = response.json()
    required = ("issuer", "authorization_endpoint", "token_endpoint", "jwks_uri")
    if obj.get("issuer") != issuer or any(not obj.get(k) for k in required):
        raise ValueError("Issuer mismatch or missing essential discovery fields")
    for key in required[1:]:
        require_https(obj[key])
    return "LIVE_PARTIAL: Discovery metadata structure verified; no code/PKCE/JWKS/conformance testing"


def probe_postgresql() -> str:
    from mt_iam.core.config import get_settings
    from mt_iam.adapters.database import Database
    cfg = get_settings()
    if not cfg.database_url or not cfg.database_url.startswith("postgresql+psycopg://"):
        raise ValueError("MT_IAM_DATABASE_URL must specify PostgreSQL psycopg")
    db = Database(cfg.database_url, pool_size=cfg.db_pool_size,
                  max_overflow=cfg.db_max_overflow, pool_timeout=cfg.db_pool_timeout)
    try:
        if not db.ping():
            raise ValueError("SELECT 1 failed")
    finally:
        db.dispose()
    return "LIVE_PARTIAL: PostgreSQL SELECT 1 works; no Supabase attribution/pooler/security verification"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Opt-in external POC connectivity probes")
    p.add_argument("kind", choices=("cloudrun", "oidc", "postgresql"))
    args = p.parse_args(argv)
    names = {"cloudrun": "MT_IAM_CLOUD_RUN_URL", "oidc": "MT_IAM_OIDC_ISSUER"}
    try:
        if args.kind == "postgresql":
            result = probe_postgresql()
        else:
            value = os.getenv(names[args.kind])
            if not value:
                print(f"BLOCKED: {names[args.kind]} not set")
                return 2
            result = probe_cloudrun_health(value) if args.kind == "cloudrun" else probe_oidc_discovery(value)
        print(result)
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__} (details/redacted URLs suppressed)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
