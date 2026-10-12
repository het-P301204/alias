# ALIAS Build Status

## Backend Foundation

**Agent 1 — Backend complete.**

All Python backend files written to `backend/alias_core/` and `scenarios/`.

### Files Created

#### Configuration
- `backend/alias_core/__init__.py` — package marker, `__version__`
- `backend/alias_core/config/settings.py` — `pydantic-settings` `Settings` class; all limits configurable via `ALIAS_*` env vars; DB path resolves to `alias/alias.db`

#### Database (`backend/alias_core/database/`)
- `models.py` — DDL constants for `experiments`, `scenario_configs`, `settings` tables
- `init_db.py` — `init_db()` creates tables in WAL mode and seeds 3 sample experiments; `get_db()` async context manager
- `queries.py` — typed CRUD: `insert_experiment`, `update_experiment_status`, `get_experiment`, `list_experiments` (paginated, filterable)

#### Experiment Engine (`backend/alias_core/experiments/`)
- `models.py` — canonical Pydantic v2 models: `ScenarioId`, `ExperimentStatus`, `LabMode`, `Evidence`, `DefenseResult`, `ExperimentConfig`, `ExperimentResult`, `ScenarioMetadata`
- `registry.py` — `ScenarioRegistry` + module-level `registry` singleton; `discover()` auto-imports from `scenarios/` package
- `engine.py` — `ExperimentEngine` + module-level `engine` singleton; `asyncio.Semaphore(3)`, `asyncio.timeout(30s)`, full lifecycle transitions persisted to SQLite; cancellation via `Task.cancel()`

#### GraphQL Lab Router (`backend/alias_core/graphql/lab_router.py`)
- FastAPI `APIRouter` at `/lab/{scenario_id}/{mode}/graphql` (POST)
- Routes each request to the scenario's `get_schema(mode)` Strawberry schema
- Schema instances cached after first load

#### Security (`backend/alias_core/security/limits.py`)
- Named constants: `MAX_QUERY_DEPTH`, `MAX_COMPLEXITY`, etc.
- `DepthLimitExtension` and `ComplexityLimitExtension` Strawberry schema extensions
- `depth_limit_extension(n)` and `complexity_limit_extension(n)` factory functions

#### API Routes (`backend/alias_core/api/routes/`)
- `health.py` — `GET /api/health`
- `scenarios.py` — `GET /api/scenarios`, `GET /api/scenarios/{id}`
- `experiments.py` — `GET /api/experiments` (paginated), `GET /api/experiments/{id}`, `POST /api/experiments`, `POST /api/experiments/{id}/cancel`
- `defenses.py` — `GET /api/defenses`, `GET /api/defenses/{id}`, `POST /api/defenses/{id}/verify`
- `reports.py` — `GET /api/reports/{id}?format=json|csv|html`

#### Middleware (`backend/alias_core/api/middleware.py`)
- CORS: `localhost:5173`, `localhost:3000`
- `ResponseSizeLimitMiddleware`: returns 413 if `Content-Length` > 1MB

#### Main App (`backend/alias_core/api/main.py`)
- FastAPI `lifespan`: calls `init_db()` then `registry.discover()`
- All routes mounted under `/api`; lab router mounted under `/lab`
- `run()` entry point for `uvicorn`

#### Scenario Protocol (`scenarios/base.py`)
- `ScenarioModule` runtime-checkable `Protocol`
- Methods: `get_metadata()`, `get_schema(mode)`, `run_experiment(config)`, `verify_defense(mode)`, `reset()`

### Seed Data
3 sample experiments seeded (is_sample=1):
1. `introspection` / vulnerable — schema fully disclosed
2. `query-complexity` / vulnerable — 4s execution, no limits
3. `field-authorization` / hardened — salary field denied to viewer role

### Dependency Notes for Agent 5 (pyproject.toml)
Add these to `[project.dependencies]`:
```
pydantic-settings>=2.3
fastapi>=0.115
strawberry-graphql[fastapi]>=0.250
httpx>=0.27
aiosqlite>=0.20
pydantic>=2.8
pyyaml>=6.0
uvicorn[standard]>=0.30
```

### Contract Notes for Other Agents
- **Agent 2 (scenarios)**: Each scenario package must expose a module-level `scenario` object satisfying `ScenarioModule` protocol. The registry's `discover()` imports `scenarios.<name>` and reads `scenario` attribute.
- **Agent 3 (frontend)**: All responses use `{ data, error, meta }` envelope. Lab GraphQL: `POST /lab/{scenario_id}/{vulnerable|hardened}/graphql`.
- **Agent 4 (CLI/tests)**: Import `alias_core.experiments.engine.engine` for experiment submission; `alias_core.experiments.registry.registry` for scenario listing.
