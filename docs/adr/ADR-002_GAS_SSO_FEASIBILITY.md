# ADR-002 — GAS + Supabase SSO Feasibility

Status: Open; POC required.

Initial baseline: GAS for identity business services, Supabase PostgreSQL for data, static Vue admin UI. Zero-cost-first and portable.

Risk: GAS Web Apps do not offer conventional response header, cookie and complete OAuth endpoint controls. Secure cross-origin SSO/OIDC is NOT proven merely by exposing an authentication API.

Options: (A) verify GAS-only full conformance if technically possible; (B) small portable protocol/cookie layer with GAS core; (C) self-hosted standards-compliant open-source protocol engine.

Select only after cross-app SSO, token/session security, performance, privacy and portability evidence. Do not deploy improvised cryptography.
