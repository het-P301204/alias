"""Async CRUD operations for the experiments table."""
import json
from typing import Optional
from datetime import datetime

import aiosqlite

from alias_core.experiments.models import (
    ExperimentResult,
    ExperimentStatus,
    LabMode,
    ScenarioId,
    Evidence,
    DefenseResult,
)


def _row_to_result(row: aiosqlite.Row) -> ExperimentResult:
    evidence_raw = row["evidence_json"]
    evidence = [Evidence(**e) for e in json.loads(evidence_raw)] if evidence_raw else []

    defense_raw = row["defensive_control_json"]
    defense = DefenseResult(**json.loads(defense_raw)) if defense_raw else None

    repro_raw = row["reproducibility_json"]
    repro = json.loads(repro_raw) if repro_raw else {}

    config_raw = row["config_json"]
    config = json.loads(config_raw) if config_raw else {}

    return ExperimentResult(
        id=row["id"],
        scenario_id=ScenarioId(row["scenario_id"]),
        mode=LabMode(row["mode"]),
        config=config,
        status=ExperimentStatus(row["status"]),
        started_at=row["started_at"] or "",
        completed_at=row["completed_at"],
        duration_ms=row["duration_ms"],
        input_summary=row["input_summary"] or "",
        expected_outcome=row["expected_outcome"] or "",
        actual_outcome=row["actual_outcome"],
        evidence=evidence,
        defensive_control_result=defense,
        error=row["error_detail"],
        reproducibility_metadata=repro,
        is_sample=bool(row["is_sample"]),
    )


async def insert_experiment(db: aiosqlite.Connection, result: ExperimentResult) -> None:
    await db.execute(
        """
        INSERT INTO experiments
        (id, scenario_id, mode, config_json, status, started_at, completed_at,
         duration_ms, input_summary, expected_outcome, actual_outcome,
         evidence_json, defensive_control_json, error_detail,
         reproducibility_json, is_sample)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            result.id,
            result.scenario_id.value,
            result.mode.value,
            json.dumps(result.config),
            result.status.value,
            result.started_at,
            result.completed_at,
            result.duration_ms,
            result.input_summary,
            result.expected_outcome,
            result.actual_outcome,
            json.dumps([e.model_dump() for e in result.evidence]),
            json.dumps(result.defensive_control_result.model_dump()) if result.defensive_control_result else None,
            result.error,
            json.dumps(result.reproducibility_metadata),
            1 if result.is_sample else 0,
        ),
    )
    await db.commit()


async def update_experiment_status(
    db: aiosqlite.Connection,
    experiment_id: str,
    status: ExperimentStatus,
    **kwargs,
) -> None:
    fields = ["status = ?"]
    values: list = [status.value]

    for key, val in kwargs.items():
        if key in ("completed_at", "duration_ms", "actual_outcome", "error_detail"):
            fields.append(f"{key} = ?")
            values.append(val)
        elif key == "evidence":
            fields.append("evidence_json = ?")
            values.append(json.dumps([e.model_dump() if hasattr(e, "model_dump") else e for e in val]))
        elif key == "defensive_control":
            fields.append("defensive_control_json = ?")
            values.append(json.dumps(val.model_dump()) if val else None)

    values.append(experiment_id)
    await db.execute(f"UPDATE experiments SET {', '.join(fields)} WHERE id = ?", values)
    await db.commit()


async def get_experiment(db: aiosqlite.Connection, experiment_id: str) -> Optional[ExperimentResult]:
    cursor = await db.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,))
    row = await cursor.fetchone()
    return _row_to_result(row) if row else None


async def list_experiments(
    db: aiosqlite.Connection,
    scenario_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[ExperimentResult], int]:
    conditions: list[str] = []
    params: list = []

    if scenario_id:
        conditions.append("scenario_id = ?")
        params.append(scenario_id)
    if status:
        conditions.append("status = ?")
        params.append(status)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    count_cursor = await db.execute(f"SELECT COUNT(*) FROM experiments {where}", params)
    count_row = await count_cursor.fetchone()
    total = count_row[0] if count_row else 0

    offset = (page - 1) * limit
    cursor = await db.execute(
        f"SELECT * FROM experiments {where} ORDER BY started_at DESC LIMIT ? OFFSET ?",
        [*params, limit, offset],
    )
    rows = await cursor.fetchall()
    return [_row_to_result(r) for r in rows], total
