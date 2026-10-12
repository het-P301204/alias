# ALIAS Design Specification
**Date:** 2026-10-11  
**Product:** ALIAS — GraphQL Security Research Platform  
**Tagline:** One endpoint. A universe of attack surfaces.  
**Status:** Approved — ready for implementation planning

---

## 1. Purpose and Scope

ALIAS is an isolated, offline-capable GraphQL security research platform. It provides six intentionally vulnerable GraphQL lab scenarios, matching hardened implementations, Python research modules, a React/TypeScript interface, a CLI, automated tests, and developer documentation. Target users are security researchers, developers, and educators working in controlled local environments.

**Not in scope:** cloud deployment, real credential testing, external target scanning, production-grade SaaS features.

---

## 2. Six Security Scenarios

| ID | Scenario | Vulnerable Weakness | Hardened Control |
|----|----------|---------------------|------------------|
| `introspection` | Schema introspection & discovery | Full introspection enabled | Introspection disabled or restricted |
| `alias-authorization` | Alias-based object authorization | Resolver authenticates caller, skips per-record ownership check | Per-record ownership verified in resolver |
| `batching` | Batching & rate limits | HTTP-level rate limiting only | GraphQL operation-count limits enforced |
| `query-complexity` | Query depth & complexity | No depth/complexity policy | Depth limits, complexity budgets, timeouts |
| `blind-recovery` | Blind schema recovery | Verbose validation errors expose field names | Production-safe error messages |
| `field-authorization` | Field-level authorization | Missing permission check on sensitive resolver | Consistent server-side field permissions |

Every scenario follows: **Understand → Configure → Execute → Observe → Analyze → Defend → Verify → Report**

---

## 3. Technology Stack

### Backend
- Python 3.12
- FastAPI
- Strawberry GraphQL
- HTTPX
- asyncio
- Pydantic v2
- SQLite (aiosqlite)
- PyYAML
- Typer + Rich (CLI)
- pytest + pytest-asyncio

### Frontend
- React 18 + TypeScript (strict)
- Vite
- Tailwind CSS
- Framer Motion
- Lucide React
- React Flow or D3 (schema graph visualization)
- Recharts (charting)
- Vitest + React Testing Library
- Playwright (e2e)

### Tooling
- ESLint + Prettier
- Ruff + mypy
- GitHub Actions CI
- SQLite schema versioning

---

## 4. Architecture

### High-Level

```
alias/
├── backend/alias_core/          # Python application
│   ├── api/                     # FastAPI routers
│   ├── config/                  # Configuration + environment
│   ├── database/                # SQLite init, models, queries
│   ├── experiments/             # Experiment lifecycle engine
│   ├── graphql/                 # Strawberry schemas (platform + scenarios)
│   ├── reporting/               # JSON, CSV, HTML report generation
│   ├── security/                # Security middleware, limits
│   └── cli/                     # Typer CLI (reuses core logic)
├── scenarios/                   # One package per scenario
│   ├── introspection/
│   ├── alias-authorization/
│   ├── batching/
│   ├── query-complexity/
│   ├── blind-recovery/
│   └── field-authorization/
├── frontend/src/                # React application
│   ├── app/                     # Router, layout, providers
│   ├── components/              # Shared UI components
│   ├── features/                # One folder per scenario + cross-cutting features
│   ├── hooks/                   # Custom React hooks
│   ├── lib/                     # Utilities
│   ├── services/                # API client layer (typed)
│   ├── styles/                  # Design tokens, global CSS
│   └── types/                   # Shared TypeScript types
└── docs/, scripts/, assets/, .github/
```

### Key Boundaries

- **Platform API** (FastAPI, `/api/*`) is separate from **Lab GraphQL endpoints** (`/lab/*/graphql`).
- Each scenario has one vulnerable GraphQL endpoint and one hardened endpoint, both served by the backend.
- The frontend never executes GraphQL queries directly to external targets — only to local lab endpoints.
- SQLite stores: experiments, settings, seeded scenario fixtures.
- All lab endpoints bind to `127.0.0.1` by default.

---

## 5. Shared Data Contracts

### Experiment Schema

```typescript
interface Experiment {
  id: string;                    // UUID
  scenario_id: ScenarioId;
  mode: 'vulnerable' | 'hardened';
  config: Record<string, unknown>;
  status: ExperimentStatus;
  started_at: string;            // ISO 8601
  completed_at: string | null;
  duration_ms: number | null;
  input_summary: string;
  expected_outcome: string;
  actual_outcome: string | null;
  evidence: Evidence[];
  defensive_control_result: DefenseResult | null;
  error: string | null;
  reproducibility_metadata: Record<string, unknown>;
}

type ExperimentStatus = 'ready' | 'validating' | 'running' | 'analyzing' | 'completed' | 'failed' | 'timeout' | 'cancelled';
type ScenarioId = 'introspection' | 'alias-authorization' | 'batching' | 'query-complexity' | 'blind-recovery' | 'field-authorization';
```

### Scenario Interface (Python)

```python
class ScenarioModule(Protocol):
    scenario_id: str
    title: str
    description: str
    vulnerable_schema: strawberry.Schema
    hardened_schema: strawberry.Schema
    default_config: dict
    
    async def run_experiment(self, config: ExperimentConfig, mode: Mode) -> ExperimentResult: ...
    async def verify_defense(self, mode: Mode) -> DefenseResult: ...
    def get_metadata(self) -> ScenarioMetadata: ...
```

---

## 6. API Contract

```
GET  /api/health
GET  /api/scenarios
GET  /api/scenarios/{scenario_id}
GET  /api/experiments                    # paginated, filterable
GET  /api/experiments/{experiment_id}
POST /api/experiments                    # start experiment
POST /api/experiments/{experiment_id}/cancel
GET  /api/defenses
GET  /api/defenses/{control_id}
POST /api/defenses/{control_id}/verify
GET  /api/reports/{experiment_id}        # returns HTML/JSON/CSV

# Lab GraphQL endpoints (separate from platform API)
POST /lab/{scenario_id}/vulnerable/graphql
POST /lab/{scenario_id}/hardened/graphql
```

All responses use consistent envelope: `{ data, error, meta }`.

---

## 7. Information Architecture (11 Pages)

1. **Overview Dashboard** — health, scenario status, recent experiments, metrics
2. **Attack Lab** — 3-panel workspace: config | query+viz | results+evidence
3. **Schema Explorer** — introspection scenario, interactive type graph
4. **Alias Authorization Lab** — alias workbench, per-record evidence table
5. **Batching & Rate Limits** — operation builder, HTTP vs operation rate comparison
6. **Query Complexity Lab** — query tree, depth viz, complexity heat map
7. **Blind Schema Recovery** — reconstruction tracker, confidence visualization
8. **Field Authorization Lab** — permission matrix, field access evidence
9. **Defense Center** — all six controls, verification, configuration
10. **Experiments & Reports** — history, search/filter, export
11. **Settings & Documentation** — configuration, CLI docs, first-run guide

---

## 8. Brand & Visual Design

**Palette:**
- Obsidian `#171615` — primary background
- Graphite `#282624` — card/panel background
- Warm Ivory `#F5F0E8` — primary text
- Muted Copper `#B97853` — accent, interactive
- Burnt Red `#B84D43` — warnings, vulnerable indicators
- Sage `#8EAA91` — success, hardened indicators
- Warm Amber `#D5A45B` — highlights, metrics

**Typography:**
- Display: DM Serif Display (headings)
- Interface: Inter (body, UI)
- Monospace: JetBrains Mono (queries, JSON, IDs, logs)

**Motion:** Framer Motion — page transitions (fade+slide), panel expansions, graph node highlight. Reduced-motion support required.

**Logo:** ALIAS wordmark + compact alias-branch symbol (inspired by GraphQL alias syntax `alias: field`).

---

## 9. Security Requirements

- Default bind: `127.0.0.1` only
- Query depth limit: configurable, default 10
- Complexity budget: configurable, default 1000
- Operation count per batch: configurable, default 10
- Execution timeout: configurable, default 30s
- Concurrency limit: max 3 simultaneous experiments
- Response size limit: 1MB per experiment result
- No arbitrary filesystem access through GraphQL
- No real credentials or external account testing
- Vulnerable fixtures contain minimum necessary weakness
- Lab reset wipes only fixture data, not platform config
- CORS restricted to localhost origins

---

## 10. Testing Requirements

### Backend (pytest)
- Health endpoint, startup, shutdown
- All 6 scenario experiment executions (vulnerable + hardened)
- Complexity calculations (deterministic assertions)
- Authorization failure detection and remediation
- Experiment persistence, cancellation, timeout
- Input validation and resource limits
- Report generation
- Security boundary enforcement (≥ 40 tests)

### Frontend (Vitest + RTL)
- Navigation, routing, layout
- Scenario selection and mode switching
- Query preview and validation
- Loading/error states
- History, search, export interactions
- Accessibility (keyboard nav, ARIA labels)

### E2E (Playwright)
- Full vulnerable→hardened workflow for each of 6 scenarios
- Report export (JSON, CSV)
- First-run experience

---

## 11. CLI Interface

```bash
alias --help
alias doctor                                          # dependency + health check
alias lab list                                        # list scenarios
alias lab start --scenario introspection              # start lab server
alias test run --scenario field-authorization         # run experiment
alias test run --scenario query-complexity --mode hardened
alias test compare --scenario alias-authorization     # compare modes
alias report list
alias report export --id <uuid> --format json
```

CLI reuses `alias_core` logic — no duplicate implementations.

---

## 12. Experiment Engine Requirements

- Unique UUID per experiment
- Lifecycle: `Ready → Validating → Running → Analyzing → Completed`
- Failure states: `failed`, `timeout`, `cancelled`
- Prevent duplicate concurrent submissions
- Cancellation releases all resources cleanly
- All timing measured server-side
- Backend owns execution truth; frontend displays returned results
- Never fabricate outcomes

---

## 13. Report Formats

Every report includes:
1. Executive summary
2. Environment (Python version, schema version, timestamp)
3. Scenario and mode
4. Methodology
5. Expected and observed results
6. Evidence (structured, per-record where applicable)
7. Defensive-control status
8. Remediation guidance
9. Limitations disclaimer (synthetic lab data)
10. Application version

Formats: JSON, CSV, HTML (polished). PDF optional if reliably implementable.

---

## 14. Acceptance Criteria (Definition of Done)

- [ ] Backend starts from fresh installation with `pip install -e .`
- [ ] Frontend builds with `npm run build` and loads at `localhost:5173`
- [ ] All 6 scenarios have working vulnerable + hardened lab endpoints
- [ ] All 6 scenarios have executable Python research runners
- [ ] Schema explorer shows actual parsed schema data
- [ ] Alias lab detects seeded ownership flaw; hardened mode denies unauthorized records
- [ ] Batching lab measures HTTP vs operation counts
- [ ] Complexity lab produces deterministic calculations; limits reject over-budget queries
- [ ] Blind recovery tracks bounded synthetic suggestions with confidence levels
- [ ] Field permission lab verifies access by role in both modes
- [ ] Defense Center runs live verification tests (not just flag checks)
- [ ] Experiments persist in SQLite across restarts
- [ ] JSON, CSV, HTML report export works
- [ ] CLI commands work and reuse core logic
- [ ] Frontend communicates with actual backend (no permanent mocks)
- [ ] Responsive layout works at 375px and 1440px
- [ ] WCAG 2.2 AA contrast targets met
- [ ] Reduced-motion respected
- [ ] ≥ 40 backend tests passing
- [ ] ≥ 20 frontend component tests passing
- [ ] 6 e2e scenario tests passing
- [ ] CI workflow runs on push (lint, type-check, test, build)
- [ ] No TODO buttons or dead navigation
- [ ] All displayed results reflect actual application state
- [ ] README verified against real installation

---

*Spec approved by user (RRP 18 submission). Proceeding to implementation planning.*
