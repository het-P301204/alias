# ALIAS — API Reference

Base URL: `http://127.0.0.1:8000`

All REST responses use the envelope:
```json
{"data": <payload>, "error": null | "message", "meta": {}}
```

---

## Health

### `GET /api/health`

Returns platform status, software version, number of loaded scenarios, and database connectivity.

**Response**
```json
{
  "data": {
    "status": "ok",
    "version": "0.1.0",
    "scenarios_loaded": 6,
    "db_ok": true,
    "timestamp": "2024-10-12T10:00:00Z"
  },
  "error": null,
  "meta": {}
}
```

---

## Scenarios

### `GET /api/scenarios`

Returns all discovered scenarios with metadata.

**Response**
```json
{
  "data": [
    {
      "id": "introspection",
      "title": "Schema Introspection",
      "description": "Discover schema internals through unrestricted introspection",
      "category": "information-disclosure",
      "difficulty": "beginner",
      "learning_objectives": ["..."],
      "default_config": {}
    }
  ],
  "error": null,
  "meta": {}
}
```

---

### `GET /api/scenarios/{scenario_id}`

Returns metadata for one scenario.

**Path params**: `scenario_id` — one of `introspection`, `alias-authorization`, `batching`, `query-complexity`, `blind-recovery`, `field-authorization`

**Response** — same shape as one item in the list above.

**404** if scenario not found.

---

## Experiments

### `GET /api/experiments`

List experiment history with optional filters.

**Query params**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `scenario_id` | string | — | Filter by scenario |
| `status` | string | — | Filter by status |
| `page` | int ≥1 | 1 | Page number |
| `limit` | int 1–100 | 20 | Page size |

**Response**
```json
{
  "data": {
    "items": [{ "id": "uuid", "scenario_id": "...", "status": "completed", ... }],
    "total": 42,
    "page": 1,
    "limit": 20
  },
  "error": null,
  "meta": {}
}
```

---

### `GET /api/experiments/{experiment_id}`

Get one experiment by UUID.

**Response** — full `ExperimentResult` object:
```json
{
  "data": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "scenario_id": "introspection",
    "mode": "vulnerable",
    "config": {},
    "status": "completed",
    "started_at": "2024-10-12T10:00:00Z",
    "completed_at": "2024-10-12T10:00:01Z",
    "duration_ms": 1240,
    "input_summary": "introspection query sent",
    "expected_outcome": "schema disclosed",
    "actual_outcome": "full schema returned",
    "evidence": [
      { "type": "graphql-response", "label": "Introspection response", "data": {...}, "timestamp": "..." }
    ],
    "defensive_control_result": null,
    "error": null,
    "reproducibility_metadata": {},
    "is_sample": false
  },
  "error": null,
  "meta": {}
}
```

**404** if not found.

---

### `POST /api/experiments`

Submit a new experiment. The engine queues it immediately (up to 3 concurrent).

**Request body**
```json
{
  "scenario_id": "introspection",
  "mode": "vulnerable",
  "parameters": {}
}
```

`scenario_id` must be a valid scenario ID. `mode` is `"vulnerable"` or `"hardened"`.

**Response** — `ExperimentResult` with `status: "ready"` or `"running"`.

**422** if validation fails (unknown scenario, invalid mode).

---

### `POST /api/experiments/{experiment_id}/cancel`

Cancel a running experiment.

**Response**
```json
{
  "data": {"cancelled": true},
  "error": null,
  "meta": {}
}
```

`cancelled: false` if the experiment was not running (already completed, not found, etc.).

---

## Defenses

### `GET /api/defenses`

List all defensive controls with descriptions.

**Response**
```json
{
  "data": [
    {
      "id": "introspection-disabled",
      "scenario_id": "introspection",
      "title": "Introspection disabled in production",
      "description": "...",
      "verification_steps": ["..."]
    }
  ],
  "error": null,
  "meta": {}
}
```

---

### `GET /api/defenses/{defense_id}`

Get one defense control.

---

### `POST /api/defenses/{defense_id}/verify`

Run the automated defense verification check. Executes the scenario's `verify_defense(mode)` call.

**Request body**
```json
{"mode": "hardened"}
```

**Response**
```json
{
  "data": {
    "control_id": "introspection-disabled",
    "verified": true,
    "description": "Introspection returns null for all types",
    "details": {"types_visible": 0, "types_expected": 0}
  },
  "error": null,
  "meta": {}
}
```

---

## Reports

### `GET /api/reports/{experiment_id}?format=json`

Export an experiment as a structured report.

**Query params**: `format` — `json` (default), `csv`, `html`

**JSON response** — full `ExperimentResult` with evidence, defense result, and metadata.

**CSV response** — flat table of evidence rows, one per line.

**HTML response** — self-contained HTML report for sharing or archiving.

**404** if experiment not found.

---

## Lab GraphQL Endpoints

Each scenario exposes a live GraphQL endpoint:

```
POST /lab/{scenario_id}/{mode}/graphql
```

Where:
- `{scenario_id}` — `introspection` | `alias-authorization` | `batching` | `query-complexity` | `blind-recovery` | `field-authorization`
- `{mode}` — `vulnerable` | `hardened`

**Request**: standard GraphQL POST body
```json
{
  "query": "{ __schema { types { name } } }",
  "variables": {}
}
```

These endpoints serve Strawberry GraphQL. The schema, available types, and enforced limits differ between modes. They are not subject to the same defensive controls as the management API.
