"""Route /lab/{scenario_id}/{mode}/graphql to the correct Strawberry schema."""
from __future__ import annotations

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import strawberry
from strawberry.fastapi import GraphQLRouter

from alias_core.experiments.models import LabMode
from alias_core.experiments.registry import registry

lab_router = APIRouter()

_schema_cache: dict[str, strawberry.Schema] = {}


def _get_schema(scenario_id: str, mode: LabMode) -> strawberry.Schema:
    cache_key = f"{scenario_id}:{mode.value}"
    if cache_key in _schema_cache:
        return _schema_cache[cache_key]

    try:
        scenario = registry.get(scenario_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id!r} not found")

    schema = scenario.get_schema(mode)
    _schema_cache[cache_key] = schema
    return schema


@lab_router.post("/{scenario_id}/{mode}/graphql")
async def lab_graphql(scenario_id: str, mode: str, request: Request) -> Response:
    try:
        lab_mode = LabMode(mode)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid mode {mode!r}; must be 'vulnerable' or 'hardened'")

    schema = _get_schema(scenario_id, lab_mode)

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    query = body.get("query", "")
    variables = body.get("variables") or {}
    operation_name = body.get("operationName")

    result = await schema.execute_async(
        query,
        variable_values=variables,
        operation_name=operation_name,
    )

    response_data: dict = {}
    if result.data is not None:
        response_data["data"] = result.data
    if result.errors:
        response_data["errors"] = [
            {"message": str(e.message), "locations": e.locations, "path": e.path}
            for e in result.errors
        ]

    return JSONResponse(content=response_data)
