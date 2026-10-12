from fastapi import APIRouter, HTTPException
from alias_core.experiments.registry import registry
from alias_core.experiments.models import LabMode

router = APIRouter()

# Static catalog of all defense controls; scenarios provide live verification.
_DEFENSE_CATALOG = [
    {
        "control_id": "introspection-disable",
        "title": "Disable Schema Introspection",
        "description": "Blocks __schema and __type queries so the schema cannot be enumerated by attackers.",
        "scenario_id": "introspection",
    },
    {
        "control_id": "alias-ownership-check",
        "title": "Per-Record Ownership Verification",
        "description": "Ensures each resolved record belongs to the authenticated caller before returning it.",
        "scenario_id": "alias-authorization",
    },
    {
        "control_id": "operation-count-limit",
        "title": "Batched Operation Count Limit",
        "description": "Enforces a maximum number of operations per HTTP request to prevent batch-amplification attacks.",
        "scenario_id": "batching",
    },
    {
        "control_id": "query-complexity-limit",
        "title": "Query Depth and Complexity Budget",
        "description": "Rejects queries that exceed configured depth or complexity thresholds before execution.",
        "scenario_id": "query-complexity",
    },
    {
        "control_id": "safe-error-messages",
        "title": "Production-Safe Error Messages",
        "description": "Returns opaque errors instead of verbose validation messages that reveal field names.",
        "scenario_id": "blind-recovery",
    },
    {
        "control_id": "field-authorization-check",
        "title": "Field-Level Permission Enforcement",
        "description": "Checks caller permissions on every sensitive resolver field before returning data.",
        "scenario_id": "field-authorization",
    },
]

_BY_ID = {d["control_id"]: d for d in _DEFENSE_CATALOG}


@router.get("/defenses")
async def list_defenses():
    return {"data": _DEFENSE_CATALOG, "error": None, "meta": {"count": len(_DEFENSE_CATALOG)}}


@router.get("/defenses/{control_id}")
async def get_defense(control_id: str):
    defense = _BY_ID.get(control_id)
    if defense is None:
        raise HTTPException(status_code=404, detail=f"Defense {control_id!r} not found")

    latest = None
    scenario_id = defense["scenario_id"]
    try:
        scenario = registry.get(scenario_id)
        latest = (await scenario.verify_defense(LabMode.HARDENED)).model_dump()
    except Exception:
        pass

    return {"data": {**defense, "latest_verification": latest}, "error": None, "meta": {}}


@router.post("/defenses/{control_id}/verify")
async def verify_defense(control_id: str):
    defense = _BY_ID.get(control_id)
    if defense is None:
        raise HTTPException(status_code=404, detail=f"Defense {control_id!r} not found")

    scenario_id = defense["scenario_id"]
    try:
        scenario = registry.get(scenario_id)
    except KeyError:
        raise HTTPException(status_code=503, detail=f"Scenario {scenario_id!r} not loaded")

    result = await scenario.verify_defense(LabMode.HARDENED)
    return {"data": result.model_dump(), "error": None, "meta": {}}
