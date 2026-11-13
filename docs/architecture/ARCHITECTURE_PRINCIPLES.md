# Architecture Principles — DRAFT

1. Independent applications: each app may use any language, server, framework and data store.
2. Central identity, decentralized business authorization: app decides admission and internal permissions.
3. MT-IAM is SSOT for shared identity attributes and directory; upstream personnel source provenance is tracked.
4. Standards-based communication: HTTPS, OIDC/OAuth, documented OpenAPI/JSON for proprietary services.
5. SSO-first UX: login once and reuse valid central session securely.
6. Central system is not on every business request path.
7. Secure defaults: least privilege, verified identity, default deny, aud/iss validation, revocation bounds.
8. Identity/security logs stay in IAM; application business logs stay with each app.
9. Portable and zero-cost-first: prove export, restore, provider migration and quotas.
10. Versioned contracts and conformance requirements for all third-party application teams.
