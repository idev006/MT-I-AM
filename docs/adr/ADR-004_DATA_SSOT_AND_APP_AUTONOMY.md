# ADR-004 — Shared Personnel SSOT and Application Autonomy
Status: PROPOSED v0.2.

## Decision
MT-IAM owns the shared identity directory and identity lifecycle. If HR is authoritative for source data, MT-IAM synchronizes and records provenance, not silently overriding HR. Client/application registration is centralized as a trust relationship. Every app owns user admission, internal role/permissions, local session, business data and business/application audit. There are no app role-permission tables in IAM.

## Why
Prevents central bottleneck and permission-schema coupling while preserving a consistent immutable user identifier and shared identity claims. Supports unlimited independent languages/hosting as an architectural intent, not a tested capacity claim.

## Consequences
App developers must validate OIDC evidence and enforce own admission server-side. They must handle stale local profile and account suspension via a documented revocation bound. Data sharing follows minimum disclosure and access-scoped APIs. Identity keys are issuer + subject, never mutable email alone.

## Rejected
A central per-app permission store and centralized approval of every app action: creates organizational coupling and runtime burden inconsistent with project requirements.
