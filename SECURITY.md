# Security Policy

ALIAS runs intentionally vulnerable GraphQL services for educational and research purposes. This document describes the safety boundaries and correct usage.

## Safety Boundaries

**Network isolation**
- All services bind to `127.0.0.1` (loopback) by default
- The backend and all lab endpoints are unreachable from other machines unless you explicitly change `ALIAS_HOST`
- Do not change the host binding to `0.0.0.0` on a shared or production network

**Data isolation**
- All fixture data is synthetic — no real credentials, PII, or production data
- The SQLite database (`alias.db`) contains only experiment history and settings
- Lab reset wipes fixture data only; platform configuration is preserved

**Endpoint isolation**
- Vulnerable lab endpoints are served under `/lab/{scenario}/{mode}/graphql`
- The platform management API (`/api/*`) enforces normal security controls
- Running a scenario in vulnerable mode affects only that lab endpoint, not the management API

**Resource limits (always enforced)**
- Maximum 3 concurrent experiments
- Experiment timeout: 30 seconds
- Response size limit: 1 MB
- Maximum batch operations: 10
- Maximum GraphQL query depth: 10 (configurable — hardened mode enforces this strictly)

## Vulnerable Mode Warning

When a scenario runs in **vulnerable** mode, the lab endpoint deliberately implements a security flaw. These endpoints:
- May disclose schema details, internal field names, or authorization logic
- May accept deeply nested or complex queries without rejection
- May not enforce field-level access controls

This is by design. The intent is to demonstrate the vulnerability in a controlled, offline environment. Do not expose these endpoints to untrusted networks.

## Reporting Issues

To report a security issue with ALIAS itself (not the intentional lab vulnerabilities), open a GitHub Issue with the label `security`. For sensitive disclosures, email the repository owner directly.

We do not accept reports about the intentional vulnerabilities in lab scenarios — those are the product.
