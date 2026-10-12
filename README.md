# ALIAS — GraphQL Security Research Platform

> One endpoint. A universe of attack surfaces.

ALIAS is an offline-capable GraphQL security research platform for understanding and demonstrating six classes of GraphQL vulnerability. Each scenario ships a deliberately vulnerable implementation alongside a hardened counterpart, so you can compare real attack behavior against effective defenses.

---

## What it does

Six independently executable lab scenarios:

| # | Scenario | What you learn |
|---|----------|----------------|
| 1 | **Schema Introspection** | Discover types, fields, mutations, and deprecated data through introspection queries |
| 2 | **Alias-Based Authorization** | Test object-level authorization failures using GraphQL field aliases |
| 3 | **Batching & Rate Limits** | Demonstrate the gap between HTTP-level and operation-level rate limiting |
| 4 | **Query Depth & Complexity** | Analyze and trigger query budget enforcement failures |
| 5 | **Blind Schema Recovery** | Reconstruct schema field names from verbose validation error messages |
| 6 | **Field-Level Authorization** | Verify consistent permission enforcement across all fields of a type |

Each scenario provides:
- **Vulnerable mode** — intentionally insecure lab endpoint
- **Hardened mode** — the same endpoint with the defensive control applied
- **Evidence capture** — structured evidence (queries, responses, timing) saved per run
- **Defense verification** — automated check that the control is actually working
- **Exportable reports** — JSON, CSV, and HTML

---

## Requirements

- Python 3.12+
- Node.js 20+
- npm 9+

---

## Installation

```bash
git clone <repo-url>
cd alias
python scripts/setup.py
```

The setup script installs Python dependencies (editable), installs frontend npm packages, and initializes the SQLite database with three sample experiments.

---

## Running

```bash
# Recommended — starts both servers concurrently
python scripts/dev.py

# Or start individually
uvicorn alias_core.api.main:app --reload   # backend  → http://127.0.0.1:8000
cd frontend && npm run dev                  # frontend → http://127.0.0.1:5173
```

Both servers must be running for the full UI to work. The backend starts first; the frontend connects immediately.

---

## CLI

```bash
# Check environment and database
alias doctor

# List available scenarios
alias lab list

# Run a scenario in vulnerable mode
alias test run --scenario introspection

# Run in hardened mode
alias test run --scenario field-authorization --mode hardened

# Compare both modes side-by-side
alias test compare --scenario alias-authorization

# List saved reports
alias report list

# Export a report
alias report export --id <uuid> --format html
alias report export --id <uuid> --format json
alias report export --id <uuid> --format csv
```

---

## Tests

```bash
# Backend unit and integration tests
pytest backend/tests/ -v

# Frontend component and hook tests
cd frontend && npm test

# Run both with one command
pytest backend/tests/ -v && (cd frontend && npm test -- --run)
```

---

## Architecture

```
Frontend (React + Vite)      http://127.0.0.1:5173
        │
        │  REST /api/*
        ▼
Backend (FastAPI)             http://127.0.0.1:8000
        │
        ├── /api/health
        ├── /api/scenarios
        ├── /api/experiments
        ├── /api/defenses
        ├── /api/reports
        │
        └── /lab/{scenario}/{mode}/graphql   ← GraphQL lab endpoints
                │
                ▼
        Experiment Engine (asyncio, semaphore, timeout)
                │
                ▼
        Scenario Modules (introspection, alias-authorization, ...)
                │
                ▼
        Strawberry GraphQL schemas (per scenario, per mode)
                │
                ▼
        SQLite (alias.db) — experiment history, settings
```

- **Backend**: FastAPI + Strawberry GraphQL + aiosqlite + Pydantic v2 + pydantic-settings
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + TanStack Query + Axios + Monaco Editor
- **Database**: SQLite (WAL mode) — loopback, file-local, no server required
- **All binding**: `127.0.0.1` only — not exposed to the network by default

Full architecture details: [docs/architecture.md](docs/architecture.md)

---

## Project layout

```
alias/
├── backend/
│   └── alias_core/          # Python package — API, engine, GraphQL router
│       ├── api/             # FastAPI routes and middleware
│       ├── config/          # pydantic-settings Settings class
│       ├── database/        # aiosqlite models, init, queries
│       ├── experiments/     # engine, registry, Pydantic models
│       ├── graphql/         # lab router (mounts per-scenario schemas)
│       └── security/        # depth/complexity limit extensions
├── scenarios/               # One package per scenario
│   ├── base.py              # ScenarioModule protocol
│   ├── introspection/
│   ├── alias_authorization/
│   ├── batching/
│   ├── query_complexity/
│   ├── blind_recovery/
│   └── field_authorization/
├── frontend/                # React + Vite app
│   └── src/
├── backend/tests/           # pytest suite
├── docs/                    # Extended documentation
├── scripts/
│   ├── setup.py             # One-command setup
│   └── dev.py               # Concurrent dev server launcher
├── .github/workflows/ci.yml
├── pyproject.toml
└── alias.db                 # Created at runtime (gitignored)
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/architecture.md](docs/architecture.md) | Service diagram, database schema, scenario lifecycle |
| [docs/installation.md](docs/installation.md) | Step-by-step for Windows, macOS, Linux |
| [docs/api.md](docs/api.md) | All 10 REST API endpoints with request/response examples |
| [docs/scenarios.md](docs/scenarios.md) | Vulnerability details for each scenario |
| [docs/defenses.md](docs/defenses.md) | Defensive controls and how to verify them |
| [docs/threat-model.md](docs/threat-model.md) | Trust boundaries, mitigations, residual risks |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Common problems and fixes |

---

## Security

This platform runs intentionally vulnerable lab services. All endpoints bind to loopback only. Fixture data is entirely synthetic. See [SECURITY.md](SECURITY.md) for the full safety policy.

---

## License

MIT — see [LICENSE](LICENSE)
