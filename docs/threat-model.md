# ALIAS — Threat Model

This document describes the trust boundaries, threats mitigated by design, and residual risks of running ALIAS.

---

## Trust Boundaries

```
┌──────────────────────────────────────────────────────────────┐
│  TRUSTED — local user / researcher                           │
│  Operates the frontend, CLI, and backend from this machine   │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTP (loopback only)
┌───────────────────────────▼──────────────────────────────────┐
│  BOUNDARY — loopback (127.0.0.1)                             │
│  All services bind here; the OS blocks remote access         │
└────────────┬──────────────────────────┬──────────────────────┘
             │                          │
┌────────────▼──────────┐   ┌───────────▼──────────────────────┐
│  Management API        │   │  Lab Endpoints                    │
│  /api/*                │   │  /lab/{scenario}/{mode}/graphql   │
│  Hardened, normal      │   │  Intentionally vulnerable (mode   │
│  FastAPI security       │   │  dependent); isolated from API    │
└────────────┬──────────┘   └───────────┬──────────────────────┘
             │                          │
┌────────────▼──────────────────────────▼──────────────────────┐
│  SQLite (alias.db)                                           │
│  Stores experiment history; no credentials; loopback only    │
└──────────────────────────────────────────────────────────────┘
```

### What is inside the trust boundary

- The researcher's browser (frontend)
- The CLI (same machine)
- The FastAPI backend process
- The SQLite database file

### What is outside the trust boundary

- Any other machine on the network (cannot reach the service by design)
- Any other user on the local machine (controlled by OS filesystem permissions)

---

## Threats Mitigated by Design

### T1 — Remote network exposure

**Threat**: An attacker on the same LAN or internet could reach and exploit the vulnerable lab endpoints.

**Mitigation**: All services bind to `127.0.0.1`. The OS rejects connections from any other address at the kernel level. Changing `ALIAS_HOST` to `0.0.0.0` is explicitly documented as unsafe and requires deliberate action.

**Residual**: None under default configuration.

---

### T2 — Sensitive data leakage from lab experiments

**Threat**: Intentionally vulnerable endpoints disclose real user data, credentials, or production secrets.

**Mitigation**: All fixture data is synthetic, generated at startup, and contains no real secrets. The SQLite database stores only experiment history (queries, responses, timing). No production API keys, passwords, or PII exist in the data layer.

**Residual**: None. Synthetic data has no value if disclosed.

---

### T3 — Resource exhaustion from crafted queries

**Threat**: A deeply nested or highly complex GraphQL query consumes all available CPU or memory.

**Mitigation**: `DepthLimitExtension` and `ComplexityLimitExtension` reject queries before resolver execution. The experiment engine enforces a 30-second timeout per experiment and a semaphore of 3 concurrent experiments. The response size middleware returns HTTP 413 for responses over 1 MB.

**Residual**: Low. Limits are configurable. A researcher can intentionally disable limits to demonstrate the attack; this is the intended use.

---

### T4 — Credential brute-force via batching

**Threat**: Batched operations multiply login attempt throughput beyond what rate limits block.

**Mitigation**: The batching scenario's hardened mode rejects batches exceeding `MAX_BATCH_OPERATIONS`. The management API does not expose authentication endpoints.

**Residual**: Vulnerable mode intentionally allows this; it is the scenario's purpose.

---

### T5 — Schema reconstruction via error messages

**Threat**: Verbose GraphQL validation errors leak field names even when introspection is disabled.

**Mitigation**: Hardened mode sanitizes all validation error messages to a generic string. Introspection-disabled hardened mode addresses both attack vectors simultaneously.

**Residual**: Vulnerable mode intentionally leaks; it is the scenario's purpose.

---

### T6 — SQLite injection

**Threat**: Experiment parameters contain SQL injection payloads that modify the database.

**Mitigation**: All database queries use parameterized statements via aiosqlite. No raw string interpolation in SQL paths.

**Residual**: None.

---

### T7 — GraphQL injection into lab schemas

**Threat**: A crafted query mutates fixture data in ways that persist across experiments.

**Mitigation**: Each experiment run is isolated. Scenarios implement `reset()` which wipes fixture data to a known state before each run. Mutations in lab schemas operate on in-memory fixture state, not SQLite.

**Residual**: Low. State persists within one experiment run but is reset before the next.

---

## Residual Risks

### R1 — Shared local machine

If multiple users share the local machine, the SQLite file (`alias.db`) and the loopback ports are accessible to any local user with filesystem/network permissions. This is a property of the local OS environment, not of ALIAS specifically.

**Recommendation**: Run ALIAS in a user account or container that other users cannot access.

---

### R2 — Intentional misconfiguration

A researcher who changes `ALIAS_HOST=0.0.0.0` exposes vulnerable lab endpoints to the network. Documentation calls this out explicitly, but ALIAS cannot prevent a deliberate misconfiguration.

**Recommendation**: Never change the host binding on a shared, cloud, or production network.

---

### R3 — CORS scope

CORS is configured to allow `localhost:5173` and `localhost:3000`. A malicious web page served from another origin cannot make credentialed cross-origin requests to the API. However, simple (non-credentialed) requests are not blocked by CORS.

**Residual**: Low — no credentials exist to steal, and the API is loopback-only.

---

### R4 — Prototype pollution via YAML config

If a future scenario loads attacker-controlled YAML (e.g., from a report export), prototype pollution could occur. Current scenarios use hardcoded fixtures; this risk is latent, not active.

**Recommendation**: Treat any user-supplied scenario config as untrusted input if custom scenario loading is added.
