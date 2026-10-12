from fastapi import APIRouter, HTTPException
from alias_core.experiments.registry import registry

router = APIRouter()


@router.get("/scenarios")
async def list_scenarios():
    return {
        "data": [s.get_metadata().model_dump() for s in registry.all()],
        "error": None,
        "meta": {"count": len(registry.all())},
    }


@router.get("/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    try:
        scenario = registry.get(scenario_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id!r} not found")
    return {
        "data": scenario.get_metadata().model_dump(),
        "error": None,
        "meta": {},
    }
