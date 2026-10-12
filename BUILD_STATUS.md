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

## Scenario Modules

All 6 security scenario modules written to `scenarios/`. Each package exposes a `scenario` singleton implementing `ScenarioModule`.

| File | Description |
|------|-------------|
| `scenarios/__init__.py` | `ALL_SCENARIOS` list + re-exports all 6 `scenario` singletons |
| `scenarios/base.py` | `ScenarioModule` Protocol definition |
| `scenarios/introspection/__init__.py` | `IntrospectionScenario` singleton |
| `scenarios/introspection/vulnerable.py` | Full Asterion Systems schema, introspection enabled |
| `scenarios/introspection/hardened.py` | `IntrospectionExtension` blocks `__schema`/`__type` |
| `scenarios/introspection/fixtures.py` | User/Product/Order/Config Strawberry types + seed data |
| `scenarios/introspection/runner.py` | Executes introspection query, counts types/fields/mutations |
| `scenarios/alias_authorization/__init__.py` | `AliasAuthorizationScenario` singleton |
| `scenarios/alias_authorization/vulnerable.py` | Order resolver — authenticated but no ownership check |
| `scenarios/alias_authorization/hardened.py` | Order resolver — `order.user_id != caller_id` raises PermissionError |
| `scenarios/alias_authorization/fixtures.py` | 3 users (alice/bob/carol), 3 orders |
| `scenarios/alias_authorization/runner.py` | Aliased query as Alice, probes own + Bob's order |
| `scenarios/batching/__init__.py` | `BatchingScenario` singleton |
| `scenarios/batching/vulnerable.py` | `authenticateUser` mutation, no operation-count limit |
| `scenarios/batching/hardened.py` | `OperationLimitExtension` — rejects >3 auth ops per request |
| `scenarios/batching/fixtures.py` | 5 synthetic demo accounts with hashed passwords |
| `scenarios/batching/runner.py` | Submits 1 request with 5 aliased auth mutations |
| `scenarios/query_complexity/__init__.py` | `QueryComplexityScenario` singleton |
| `scenarios/query_complexity/vulnerable.py` | Relational schema (User→Post→Comment→author) no limits |
| `scenarios/query_complexity/hardened.py` | `MaxDepthExtension(5)` + `MaxComplexityExtension(100)` |
| `scenarios/query_complexity/fixtures.py` | 3 users × 3 posts × 3 comments |
| `scenarios/query_complexity/runner.py` | 3 queries: shallow/medium/deep; `calculate_depth` + `estimate_complexity` |
| `scenarios/blind_recovery/__init__.py` | `BlindRecoveryScenario` singleton |
| `scenarios/blind_recovery/vulnerable.py` | `SecretDocument` type; Strawberry default verbose errors |
| `scenarios/blind_recovery/hardened.py` | `SanitizeErrorExtension` strips "Did you mean" from errors |
| `scenarios/blind_recovery/fixtures.py` | 5 secret field names + 50 probe candidates |
| `scenarios/blind_recovery/runner.py` | Probes all 50 candidates, tracks "Did you mean" leaks |
| `scenarios/field_authorization/__init__.py` | `FieldAuthorizationScenario` singleton |
| `scenarios/field_authorization/vulnerable.py` | `salary` has ADMIN guard, `ssn` has **no guard** (flaw) |
| `scenarios/field_authorization/hardened.py` | `ssn` resolver now enforces ADMIN-only |
| `scenarios/field_authorization/fixtures.py` | 4 role-tiered profiles (GUEST/CUSTOMER/STAFF/ADMIN) |
| `scenarios/field_authorization/runner.py` | Queries as Alice (CUSTOMER), checks per-field access vs policy |

## DevOps & Docs

**Agent 5 (DevOps) — Complete.**

All project-level configuration, CI, scripts, and documentation written.

### Files Created

#### Project configuration
- `pyproject.toml` — `pydantic-settings>=2.3` added; `[project.optional-dependencies] dev`; `setuptools.package-dir` maps `alias_core` → `backend/alias_core`
- `.gitignore` — Python + Node + IDE + `alias.db`
- `.env.example` — all `ALIAS_*` env vars with defaults

#### Scripts
- `scripts/setup.py` — cross-platform: pip install → npm install → init_db; prints start instructions
- `scripts/dev.py` — starts backend + frontend concurrently; monitors both processes; clean Ctrl+C shutdown

#### CI
- `.github/workflows/ci.yml` — two jobs: `backend` (ruff + mypy + pytest) and `frontend` (tsc + build + vitest)

#### Legal / security
- `LICENSE` — MIT, copyright ALIAS Contributors
- `SECURITY.md` — safety boundaries, loopback binding policy, vulnerable-mode warning

#### Documentation (`docs/`)
- `docs/architecture.md` — ASCII service diagram, database schema, scenario lifecycle state machine, security boundaries
- `docs/installation.md` — step-by-step for Windows, macOS, Linux; virtual environment guidance; verification curl commands
- `docs/api.md` — all 10 REST endpoints + lab GraphQL; request/response examples with envelope format
- `docs/scenarios.md` — all 6 vulnerabilities: what is demonstrated, why it matters, hardened mode explanation
- `docs/defenses.md` — all 6 defensive controls: description, how to verify, passing criteria, code pseudocode
- `docs/threat-model.md` — trust boundaries, 7 threats mitigated by design, 4 residual risks
- `docs/troubleshooting.md` — 12 common problems with platform-specific fix commands

#### Root docs
- `README.md` — full project README: feature table, requirements, install, run, CLI, tests, architecture diagram, project layout, docs table

## Frontend

**Agent 3 (Frontend) — Complete.**

React 18 + TypeScript + Vite 5 + Tailwind CSS 3 frontend. All 11 pages implemented and verified in the browser at `http://localhost:5180`. Build passes (`tsc && vite build` clean, 993KB bundle). TypeScript strict mode passes with 0 errors.

### Pages (11 total)
1. `/` — Overview Dashboard: health status, 6 scenario cards, metrics row, recent experiments table
2. `/lab` — Attack Lab: 3-panel workspace (config/Monaco editor/results), status polling, evidence accordion
3. `/schema` — Schema Explorer: React Flow type graph, searchable type list, kind filter chips, hardened "Introspection Disabled" state
4. `/alias` — Alias Authorization Lab: user/order selector, alias count stepper, generated query preview, authorization results table
5. `/batching` — Batching & Rate Limits: operation slider, dual metric cards, Recharts breakdown chart, execution timeline
6. `/complexity` — Query Complexity Lab: shallow/medium/deep presets, complexity calculator, field cost heatmap, execution time chart
7. `/blind-recovery` — Blind Schema Recovery: 50-candidate grid with status chips, discovery progress bar, evidence accordion
8. `/field-auth` — Field Authorization Lab: role card selector, full permission matrix with vulnerable SSN row highlighted
9. `/defense` — Defense Center: 6 control cards with config values, vulnerable/hardened behavior comparison, Verify Now button
10. `/experiments` — Experiments & Reports: search/filter/paginate, detail drawer with full JSON viewer, export (JSON/CSV/HTML), re-run
11. `/settings` — Settings & Documentation: backend URL config, 8-step first-run guide, CLI reference, architecture diagram, scenario guides accordion, troubleshooting

### Key Files
- `frontend/src/main.tsx` — entry point, QueryClient setup
- `frontend/src/App.tsx` — AnimatePresence page transitions
- `frontend/src/app/Layout.tsx` — sidebar nav (240px), top bar with VULNERABLE/HARDENED badge
- `frontend/src/app/router.tsx` — React Router v6 routes
- `frontend/src/services/api.ts` — Axios instance + typed API functions
- `frontend/src/hooks/useApi.ts` — TanStack Query hooks with 2s polling for active experiments
- `frontend/src/hooks/useExperiment.ts` — experiment runner hook (start/cancel/reset)
- `frontend/src/components/ui/Badge.tsx` — 16 variants (status, mode, difficulty)
- `frontend/src/components/ui/Button.tsx` — primary/secondary/ghost/danger with loading spinner
- `frontend/src/components/ui/Card.tsx` — hover scale + border color shift
- `frontend/src/components/ui/Drawer.tsx` — Framer Motion slide-in, Esc to close
- `frontend/src/components/ui/StatusIndicator.tsx` — lifecycle stepper with icons
- `frontend/src/components/ui/JsonViewer.tsx` — syntax-highlighted JSON (no dependencies)
- `frontend/src/components/ui/MetricCard.tsx` — large number + trend indicator
- `frontend/src/components/ui/LoadingSkeleton.tsx` — animated pulse placeholders
- `frontend/src/components/ui/ModeToggle.tsx` — VULNERABLE/HARDENED toggle
- `frontend/src/components/visualization/SchemaGraph.tsx` — React Flow wrapper
- `frontend/src/components/visualization/ComplexityHeatMap.tsx` — Recharts field cost bars
- `frontend/src/components/visualization/BatchTimeline.tsx` — accepted/rejected operation bars
- `frontend/src/index.css` — CSS custom properties, scrollbar styles, reduced-motion support

### Design System
- Colors: obsidian/graphite/copper/sage/amber/red tokens via Tailwind + CSS vars
- Fonts: DM Serif Display (headings), Inter (UI), JetBrains Mono (code)
- Animations: Framer Motion page transitions, hover scale 1.01, status pulse

### Config
- `frontend/package.json`, `vite.config.ts`, `tsconfig.json`, `tailwind.config.ts`, `postcss.config.js`
- Dev server: port 5180 (added to `.claude/launch.json`)

## CLI & Tests

**Agent 4 (CLI & Tests) — Complete.**

Typer+Rich CLI, JSON/CSV/HTML report generator, and full pytest suite. All 6 scenario implementations confirmed (3 written by Agent 2, 3 written by Agent 4 to fill gaps).

### CLI (`backend/alias_core/cli/main.py`)

Entry point: `alias_core.cli.main:app`

Sub-apps and commands:

| Command | Description |
|---------|-------------|
| `alias doctor` | Health check: Python ≥ 3.12, key imports, DB path, port 8000 free |
| `alias lab list` | Rich table of all 6 scenario IDs, names, categories, difficulty |
| `alias lab start` | Launch uvicorn dev server (`localhost:8000`) |
| `alias test run --scenario <id> [--mode vulnerable\|hardened] [--json]` | Run one scenario experiment; print Rich table or raw JSON |
| `alias test compare --scenario <id>` | Run both modes side-by-side for diff |
| `alias report list [--limit N]` | List experiments from SQLite DB |
| `alias report export --id <uuid> --format json\|csv\|html [--output <path>]` | Export one experiment as report |

### Report Generator (`backend/alias_core/reporting/generator.py`)

Three functions, each accepts an `ExperimentResult` and returns a string:

- `generate_json(result)` — structured JSON with executive summary, methodology, findings, evidence, remediation, and limitations sections
- `generate_csv(result)` — evidence rows as CSV (type, label, timestamp, data columns)
- `generate_html(result)` — self-contained dark HTML report (`#171615` background, `#d5a45b` accent), all sections inline

### Scenario Completions (Agent 4)

Three scenario packages were missing implementations and were written by Agent 4:

**`scenarios/query_complexity/`** — Strawberry schema with User→Post→Comment→Author chain; `calculate_depth()` (graphql.parse + recursive traversal) and `estimate_complexity()` (list_multiplier exponential growth); depth limit 4 in hardened mode rejects depth-5 queries.

**`scenarios/blind_recovery/`** — Verbose runtime errors in vulnerable mode (`"valid ids are: ['u1','u2','u3']"`); hardened mode returns `None` instead of raising. Runner probes two non-existent entity IDs, records `reveals_suggestion` per error.

**`scenarios/field_authorization/`** — Employee type with `ssn`/`salary`; vulnerable exposes all fields unconditionally; hardened checks `info.context["role"]` against a policy table. Runner queries as a `viewer`-role caller.

### Test Suite (`backend/tests/`)

86 tests total across 7 modules:

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_health.py` | 7 | Health endpoint, data envelope, version, `scenarios_loaded == 6`, DB ok |
| `test_experiments.py` | 12 | CRUD, pagination, filtering, cancel, 404 for nonexistent |
| `test_security.py` | 10 | CORS (evil origin blocked, localhost:5173 allowed), 422 validation, HTML injection |
| `test_reports.py` | 9 | HTTP export + generator unit tests for JSON/CSV/HTML; seeded UUID5 experiment IDs |
| `test_scenarios/test_introspection.py` | 13 | `type="schema_dump"` evidence, type/field counts, hardened blocks introspection |
| `test_scenarios/test_alias_authorization.py` | 9 | IDOR detection: `authorized=False` and `actually_returned=True` |
| `test_scenarios/test_batching.py` | 8 | 5 ops accepted in vulnerable; `rate_limit_triggered=True` in hardened |
| `test_scenarios/test_query_complexity.py` | 16 | Unit: `calculate_depth`, `estimate_complexity`; integration: depth-5 rejected in hardened |
| `test_scenarios/test_blind_recovery.py` | 10 | `reveals_suggestion=True` in vulnerable; `=False` for all probes in hardened |
| `test_scenarios/test_field_authorization.py` | 12 | SSN exposed in vulnerable; `actual_access=False` for ssn/salary in hardened |

Tests use `asyncio.run()` for async scenario calls (no pytest-asyncio dependency). Seeded UUID5 IDs used for report tests to avoid waiting for completed experiments.
