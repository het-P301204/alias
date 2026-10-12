"""Experiment execution engine with lifecycle management."""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional

from alias_core.experiments.models import (
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    LabMode,
    ScenarioId,
)
from alias_core.experiments.registry import ScenarioRegistry, registry as _default_registry
from alias_core.config.settings import settings
from alias_core.database.init_db import get_db
from alias_core.database.queries import insert_experiment, update_experiment_status, get_experiment


class ExperimentEngine:
    def __init__(self, scenario_registry: Optional[ScenarioRegistry] = None) -> None:
        self._registry = scenario_registry or _default_registry
        self._semaphore = asyncio.Semaphore(settings.max_concurrent_experiments)
        self._running_tasks: dict[str, asyncio.Task] = {}

    async def submit(self, config: ExperimentConfig) -> ExperimentResult:
        now = datetime.now(timezone.utc).isoformat()
        experiment_id = str(uuid.uuid4())

        result = ExperimentResult(
            id=experiment_id,
            scenario_id=config.scenario_id,
            mode=config.mode,
            config=config.parameters,
            status=ExperimentStatus.READY,
            started_at=now,
        )

        async with get_db() as db:
            await insert_experiment(db, result)

        task = asyncio.create_task(self._run(experiment_id, config))
        self._running_tasks[experiment_id] = task
        task.add_done_callback(lambda t: self._running_tasks.pop(experiment_id, None))

        return result

    async def _run(self, experiment_id: str, config: ExperimentConfig) -> None:
        async with self._semaphore:
            await self._transition(experiment_id, ExperimentStatus.VALIDATING)

            try:
                scenario = self._registry.get(config.scenario_id.value)
            except KeyError as exc:
                await self._fail(experiment_id, str(exc))
                return

            await self._transition(experiment_id, ExperimentStatus.RUNNING)

            try:
                async with asyncio.timeout(settings.experiment_timeout_seconds):
                    raw_result = await scenario.run_experiment(config)
            except TimeoutError:
                await self._timeout(experiment_id)
                return
            except asyncio.CancelledError:
                await self._cancel(experiment_id)
                return
            except Exception as exc:
                await self._fail(experiment_id, str(exc))
                return

            await self._transition(experiment_id, ExperimentStatus.ANALYZING)

            completed_at = datetime.now(timezone.utc).isoformat()
            start_dt = datetime.fromisoformat(raw_result.started_at.replace("Z", "+00:00")) if raw_result.started_at else datetime.now(timezone.utc)
            end_dt = datetime.now(timezone.utc)
            duration_ms = int((end_dt - start_dt).total_seconds() * 1000)

            async with get_db() as db:
                await update_experiment_status(
                    db,
                    experiment_id,
                    ExperimentStatus.COMPLETED,
                    completed_at=completed_at,
                    duration_ms=duration_ms,
                    actual_outcome=raw_result.actual_outcome,
                    evidence=raw_result.evidence,
                    defensive_control=raw_result.defensive_control_result,
                )

    async def _transition(self, experiment_id: str, status: ExperimentStatus) -> None:
        async with get_db() as db:
            await update_experiment_status(db, experiment_id, status)

    async def _fail(self, experiment_id: str, error: str) -> None:
        async with get_db() as db:
            await update_experiment_status(
                db, experiment_id, ExperimentStatus.FAILED,
                completed_at=datetime.now(timezone.utc).isoformat(),
                error_detail=error,
            )

    async def _timeout(self, experiment_id: str) -> None:
        async with get_db() as db:
            await update_experiment_status(
                db, experiment_id, ExperimentStatus.TIMEOUT,
                completed_at=datetime.now(timezone.utc).isoformat(),
                error_detail=f"Experiment timed out after {settings.experiment_timeout_seconds}s",
            )

    async def _cancel(self, experiment_id: str) -> None:
        async with get_db() as db:
            await update_experiment_status(
                db, experiment_id, ExperimentStatus.CANCELLED,
                completed_at=datetime.now(timezone.utc).isoformat(),
            )

    async def cancel(self, experiment_id: str) -> bool:
        task = self._running_tasks.get(experiment_id)
        if task and not task.done():
            task.cancel()
            return True
        return False

    async def get(self, experiment_id: str) -> Optional[ExperimentResult]:
        async with get_db() as db:
            return await get_experiment(db, experiment_id)


engine = ExperimentEngine()
