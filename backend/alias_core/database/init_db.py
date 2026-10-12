import json
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta

import aiosqlite

from .models import EXPERIMENTS_DDL, SCENARIO_CONFIGS_DDL, SETTINGS_DDL
from alias_core.config.settings import settings

_DB_PATH = settings.db_path


@asynccontextmanager
async def get_db():
    async with aiosqlite.connect(_DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        yield db


async def init_db() -> None:
    async with aiosqlite.connect(_DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")

        await db.execute(EXPERIMENTS_DDL)
        await db.execute(SCENARIO_CONFIGS_DDL)
        await db.execute(SETTINGS_DDL)
        await db.commit()

        await _seed_sample_experiments(db)


async def _seed_sample_experiments(db: aiosqlite.Connection) -> None:
    cursor = await db.execute("SELECT COUNT(*) FROM experiments WHERE is_sample=1")
    row = await cursor.fetchone()
    if row and row[0] >= 3:
        return

    now = datetime.now(timezone.utc)

    samples = [
        {
            "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, "alias-sample-introspection")),
            "scenario_id": "introspection",
            "mode": "vulnerable",
            "config_json": json.dumps({"query": "__schema { types { name } }"}),
            "status": "completed",
            "started_at": (now - timedelta(hours=2)).isoformat(),
            "completed_at": (now - timedelta(hours=2) + timedelta(seconds=1, milliseconds=240)).isoformat(),
            "duration_ms": 1240,
            "input_summary": "Full introspection query against vulnerable endpoint",
            "expected_outcome": "Schema fully disclosed: all types, fields, and directives returned",
            "actual_outcome": "Schema disclosed — 42 types returned including internal admin types",
            "evidence_json": json.dumps([
                {
                    "type": "graphql_response",
                    "label": "Introspection response",
                    "data": {"data": {"__schema": {"types": [{"name": "Query"}, {"name": "AdminMutation"}, {"name": "InternalUser"}]}}},
                    "timestamp": (now - timedelta(hours=2)).isoformat(),
                },
                {
                    "type": "field_list",
                    "label": "Sensitive types discovered",
                    "data": ["AdminMutation", "InternalUser", "SecretConfig"],
                    "timestamp": (now - timedelta(hours=2)).isoformat(),
                },
            ]),
            "defensive_control_json": None,
            "error_detail": None,
            "reproducibility_json": json.dumps({"tool": "curl", "command": 'curl -X POST http://127.0.0.1:8000/lab/introspection/vulnerable/graphql -H "Content-Type: application/json" -d \'{"query":"{__schema{types{name}}}"}\''}),
            "is_sample": 1,
        },
        {
            "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, "alias-sample-query-complexity")),
            "scenario_id": "query-complexity",
            "mode": "vulnerable",
            "config_json": json.dumps({"depth": 8, "width": 5}),
            "status": "completed",
            "started_at": (now - timedelta(hours=1)).isoformat(),
            "completed_at": (now - timedelta(hours=1) + timedelta(seconds=4, milliseconds=87)).isoformat(),
            "duration_ms": 4087,
            "input_summary": "Deeply nested query (depth=8, width=5) with no server-side limits",
            "expected_outcome": "Query accepted; server spends excessive CPU resolving nested data",
            "actual_outcome": "Query accepted — resolver executed 5^8=390,625 field resolutions; no rejection",
            "evidence_json": json.dumps([
                {
                    "type": "timing",
                    "label": "Server execution time",
                    "data": {"duration_ms": 4087, "cpu_percent": 92.4},
                    "timestamp": (now - timedelta(hours=1)).isoformat(),
                },
                {
                    "type": "complexity_score",
                    "label": "Calculated complexity",
                    "data": {"depth": 8, "width": 5, "total_fields": 390625, "limit": None},
                    "timestamp": (now - timedelta(hours=1)).isoformat(),
                },
            ]),
            "defensive_control_json": None,
            "error_detail": None,
            "reproducibility_json": json.dumps({"tool": "python", "script": "scenarios/query-complexity/runner.py"}),
            "is_sample": 1,
        },
        {
            "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, "alias-sample-field-authorization")),
            "scenario_id": "field-authorization",
            "mode": "hardened",
            "config_json": json.dumps({"role": "viewer", "target_field": "salary"}),
            "status": "completed",
            "started_at": (now - timedelta(minutes=30)).isoformat(),
            "completed_at": (now - timedelta(minutes=30) + timedelta(milliseconds=380)).isoformat(),
            "duration_ms": 380,
            "input_summary": "Viewer-role token requesting salary field on hardened endpoint",
            "expected_outcome": "Field access denied; null returned with permission error extension",
            "actual_outcome": "Field denied — PERMISSION_DENIED error in extensions; salary=null",
            "evidence_json": json.dumps([
                {
                    "type": "graphql_response",
                    "label": "Hardened endpoint response",
                    "data": {"data": {"user": {"id": "u1", "name": "Alice", "salary": None}}, "errors": [{"message": "Permission denied", "extensions": {"code": "PERMISSION_DENIED", "field": "salary"}}]},
                    "timestamp": (now - timedelta(minutes=30)).isoformat(),
                },
                {
                    "type": "permission_matrix",
                    "label": "Role → field access",
                    "data": {"viewer": {"name": True, "email": True, "salary": False}, "admin": {"name": True, "email": True, "salary": True}},
                    "timestamp": (now - timedelta(minutes=30)).isoformat(),
                },
            ]),
            "defensive_control_json": json.dumps({
                "control_id": "field-authorization-check",
                "verified": True,
                "description": "Per-field permission enforcement",
                "details": {"role": "viewer", "field": "salary", "denied": True},
            }),
            "error_detail": None,
            "reproducibility_json": json.dumps({"tool": "alias", "command": "alias test run --scenario field-authorization --mode hardened"}),
            "is_sample": 1,
        },
    ]

    for s in samples:
        await db.execute(
            """
            INSERT OR IGNORE INTO experiments
            (id, scenario_id, mode, config_json, status, started_at, completed_at,
             duration_ms, input_summary, expected_outcome, actual_outcome,
             evidence_json, defensive_control_json, error_detail,
             reproducibility_json, is_sample)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                s["id"], s["scenario_id"], s["mode"], s["config_json"],
                s["status"], s["started_at"], s["completed_at"],
                s["duration_ms"], s["input_summary"], s["expected_outcome"],
                s["actual_outcome"], s["evidence_json"], s["defensive_control_json"],
                s["error_detail"], s["reproducibility_json"], s["is_sample"],
            ),
        )
    await db.commit()
