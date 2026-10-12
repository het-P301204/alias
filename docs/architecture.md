# ALIAS — Architecture

## Service Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (localhost)                      │
│                React 18 + Vite + TypeScript                 │
│               http://127.0.0.1:5173                         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP (REST + fetch)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                FastAPI Backend                               │
│               http://127.0.0.1:8000                         │
│                                                             │
│  ┌─────────────────┐   ┌──────────────────────────────────┐ │
│  │  /api/* routes  │   │  /lab/{scenario}/{mode}/graphql   │ │
│  │                 │   │  (Strawberry GraphQL endpoint)    │ │
│  │  health         │   └───────────────┬──────────────────┘ │
│  │  scenarios      │                   │                     │
│  │  experiments    │   ┌───────────────▼──────────────────┐ │
│  │  defenses       │   │       Lab Router                 │ │
│  │  reports        │   │  routes req → scenario schema    │ │
│  └────────┬────────┘   └───────────────┬──────────────────┘ │
│           │                            │                     │
│  ┌────────▼────────────────────────────▼──────────────────┐ │
│  │              Experiment Engine                          │ │
│  │  asyncio.Semaphore(3) · asyncio.timeout(30s)           │ │
│  │  lifecycle: ready→validating→running→analyzing→done     │ │
│  └────────────────────────┬───────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐ │
│  │              Scenario Registry                          │ │
│  │  auto-discovers scenarios/ package at startup          │ │
│  └────────────────────────┬───────────────────────────────┘ │
│                           │                                  │
│  ┌──────────┬─────────────┴──┬────────────┬───────────────┐ │
│  │introspect│alias-authoriztn│  batching  │query-complexty│ │
│  ├──────────┼────────────────┼────────────┼───────────────┤ │
│  │blind-rec.│field-authoriztn│            │               │ │
│  └──────────┴────────────────┴────────────┴───────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐ │
│  │     Strawberry GraphQL (per scenario, per mode)        │ │
│  │     vulnerable schema  |  hardened schema              │ │
│  └────────────────────────┬───────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐ │
│  │                  aiosqlite (alias.db)                  │ │
│  │   experiments · scenario_configs · settings            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

**`experiments`** — one row per experiment run
```sql
id TEXT PRIMARY KEY               -- UUID v4
scenario_id TEXT NOT NULL         -- e.g. "introspection"
mode TEXT NOT NULL                -- "vulnerable" | "hardened"
status TEXT NOT NULL              -- ExperimentStatus enum value
config_json TEXT NOT NULL         -- ExperimentConfig serialized
result_json TEXT                  -- ExperimentResult when complete
started_at TEXT NOT NULL          -- ISO 8601 UTC
completed_at TEXT                 -- ISO 8601 UTC, nullable
is_sample INTEGER DEFAULT 0       -- 1 for pre-seeded demo rows
```

**`scenario_configs`** — persisted per-scenario settings
```sql
scenario_id TEXT PRIMARY KEY
config_json TEXT NOT NULL
updated_at TEXT NOT NULL
```

**`settings`** — key/value store for platform preferences
```sql
key TEXT PRIMARY KEY
value TEXT NOT NULL
```

Three sample rows are seeded on first run: one introspection run (vulnerable), one query-complexity run (vulnerable), one field-authorization run (hardened).

## Scenario Lifecycle

Each experiment transitions through a fixed state machine:

```
ready
  │  (engine accepts the config)
  ▼
validating
  │  (scenario_id exists in registry, mode is valid)
  ▼
running
  │  (scenario.run_experiment() executes under semaphore + timeout)
  ▼
analyzing
  │  (scenario assembles evidence, calls verify_defense)
  ▼
completed   ←→  failed
                timeout
                cancelled
```

State transitions are written to SQLite immediately, so the frontend polling `/api/experiments/{id}` always sees current status.

## Security Boundaries

```
┌────────────────────────────────────┐
│  Platform API  /api/*              │  Normal FastAPI security
│  CORS: localhost:5173 only         │  No intentional vulnerabilities
│  ResponseSizeLimitMiddleware 1MB   │
├────────────────────────────────────┤
│  Lab Endpoints  /lab/*             │  Intentionally vulnerable (when mode=vulnerable)
│  Per-scenario Strawberry schemas   │  Isolated from platform API
│  Depth/complexity limits optional  │  Fixture data only — no real secrets
├────────────────────────────────────┤
│  SQLite alias.db                   │  Local file, WAL mode
│  No auth — loopback only           │  Experiment history, no credentials
└────────────────────────────────────┘
         All bind to 127.0.0.1
```

The platform management API (`/api/*`) is always hardened. Only the lab endpoints (`/lab/*/vulnerable/graphql`) implement intentional flaws — and only when the scenario explicitly runs in vulnerable mode. The two endpoint trees share no authentication state or database credentials.
