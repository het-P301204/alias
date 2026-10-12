from fastapi import APIRouter, HTTPException, Query
from alias_core.experiments.models import ExperimentConfig
from alias_core.experiments.engine import engine
from alias_core.database.init_db import get_db
from alias_core.database.queries import get_experiment, list_experiments

router = APIRouter()


@router.get("/experiments")
async def list_experiments_route(
    scenario_id: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    async with get_db() as db:
        items, total = await list_experiments(db, scenario_id=scenario_id, status=status, page=page, limit=limit)
    return {
        "data": {
            "items": [i.model_dump() for i in items],
            "total": total,
            "page": page,
            "limit": limit,
        },
        "error": None,
        "meta": {},
    }


@router.get("/experiments/{experiment_id}")
async def get_experiment_route(experiment_id: str):
    async with get_db() as db:
        result = await get_experiment(db, experiment_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Experiment {experiment_id!r} not found")
    return {"data": result.model_dump(), "error": None, "meta": {}}


@router.post("/experiments")
async def create_experiment(config: ExperimentConfig):
    result = await engine.submit(config)
    return {"data": result.model_dump(), "error": None, "meta": {}}


@router.post("/experiments/{experiment_id}/cancel")
async def cancel_experiment(experiment_id: str):
    cancelled = await engine.cancel(experiment_id)
    return {"data": {"cancelled": cancelled}, "error": None, "meta": {}}
