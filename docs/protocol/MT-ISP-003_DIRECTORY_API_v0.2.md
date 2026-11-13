# MT-ISP-003 — Directory and Client Service API Contract v0.2
Status: DRAFT logical contract; endpoint names are **not deployed GAS routes**.

## API boundaries
OIDC provider protocol endpoints are not replaced by generic auth/verify JSON APIs. Directory APIs retrieve/minimize identity data after independent token and scope validation. Client registration/admin endpoints require privileged service identity.

## Proposed routes (illustrative)
| Method | Route | Purpose | Scope |
|---|---|---|---|
| GET | /v1/identity/me | My minimal directory profile | profile:read |
| GET | /v1/directory/users/{user_id} | Approved directory lookup | directory:read |
| GET | /v1/organizations | Minimal organization hierarchy | org:read |
| GET | /v1/directory/changes?cursor=... | Authorized delta sync | directory:sync |
| POST | /v1/admin/clients | Register app client | platform:client.manage |
| PATCH | /v1/admin/accounts/{user_id}/status | Account suspend/activate | platform:account.manage |
| GET | /v1/admin/audit | Read constrained security audit | platform:audit.read |

## Transport and authentication
- HTTPS. For cross-origin browsers, permitted origins and CORS must be explicit in a standards-capable edge/runtime (GAS response header limitations apply).
- Caller identity MUST be established from verified protocol evidence. Never trust body user_id or browser-supplied app_id as authentication.
- Use content-type application/json, UUID request_id, UTC timestamp, correlation_id.
- No direct Supabase service-key access by independent applications.

## Example authorized minimal profile response
```json
{
  "user_id": "00000000-0000-4000-8000-000000000001",
  "display_name": "Synthetic User",
  "organization_id": "00000000-0000-4000-8000-000000000002",
  "account_status": "active",
  "profile_version": 3
}
```

## Error contract
```json
{"error":{"code":"FORBIDDEN","message":"Access denied","request_id":"req-example","retryable":false}}
```
Recommended semantic responses: 400 malformed; 401 unauthenticated; 403 forbidden; 404 not found (avoid account enumeration); 409 conflict; 429 limited; 503 unavailable. Error behavior is a target gateway contract, **not proof GAS can set these status codes**.

## Changes and sync
- Change cursor is opaque, scoped to caller, supports bounded pages; expire/rebuild when retention exceeded.
- An app may cache only allowed fields with TTL, source timestamp and profile version; outdated data must not silently grant new privileges.
- Data changed at IAM does not update application-owned roles.
- Directory APIs must provide filtering/pagination and measurable rate limit; do not expose unbounded exports to arbitrary clients.

## Versioning and compatibility
- Additive fields are allowed in v1 with tolerant-reader clients.
- Breaking changes require new API major version or explicitly agreed migration; old and new can coexist during a bounded transition.
- Schema, examples and negative tests must be published as machine-readable OpenAPI before production.
