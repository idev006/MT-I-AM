import httpx
import pytest
from mt_iam.poc import live_probes


def test_discovery_rejects_untrusted_scheme_and_credentials():
    for url in ("http://issuer.example", "https://user:password@issuer.example", "ftp://x.example"):
        with pytest.raises(ValueError):
            live_probes.require_https(url)


def test_oidc_discovery_structure_with_fake_transport(monkeypatch):
    class FakeClient:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def get(self, uri):
            req = httpx.Request("GET", uri)
            return httpx.Response(200, request=req, json={
                "issuer": "https://issuer.example",
                "authorization_endpoint": "https://issuer.example/authorize",
                "token_endpoint": "https://issuer.example/token",
                "jwks_uri": "https://issuer.example/jwks",
            })
    monkeypatch.setattr(live_probes.httpx, "Client", FakeClient)
    assert live_probes.probe_oidc_discovery("https://issuer.example").startswith("LIVE_PARTIAL")


def test_oidc_discovery_rejects_wrong_issuer(monkeypatch):
    class FakeClient:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def get(self, uri):
            return httpx.Response(200, request=httpx.Request("GET", uri), json={
                "issuer": "https://wrong.example", "authorization_endpoint": "https://issuer.example/authorize",
                "token_endpoint": "https://issuer.example/token", "jwks_uri": "https://issuer.example/jwks",
            })
    monkeypatch.setattr(live_probes.httpx, "Client", FakeClient)
    with pytest.raises(ValueError):
        live_probes.probe_oidc_discovery("https://issuer.example")
