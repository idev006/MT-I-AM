# ADR-001 — Central Identity, Independent App Authorization

Status: Proposed.

Decision: MT-IAM owns identity, SSO, minimal shared personnel directory and client registry. Each app independently decides who may enter it, what roles/actions are allowed, and stores business logs/data. Apps have technology and hosting independence.

Consequences: All apps use common identity and security contracts and enforce local authorization on backend. MT-IAM does not store per-app role/permission matrices.
