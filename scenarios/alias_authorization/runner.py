import time
import uuid
from datetime import datetime, timezone

from alias_core.experiments.models import (
    ExperimentConfig, ExperimentResult, ExperimentStatus,
    Evidence, DefenseResult, LabMode,
)
from alias_core.experiments.models import ScenarioId

# Alice (id=1) accesses her own order (1) and Bob's order (3)
ALIASED_QUERY = """
{
  myOrder: order(id: "1") { id total userId }
  bobsOrder: order(id: "3") { id total userId }
}
"""

# Corrected field name for Strawberry snake_case → camelCase mapping
ALIASED_QUERY_SNAKE = """
{
  myOrder: order(id: "1") { id total status }
  bobsOrder: order(id: "3") { id total status }
}
"""

ALICE_CTX = {"user_id": "1"}


def _get_schema(mode: LabMode):
    if mode == LabMode.VULNERABLE:
        from scenarios.alias_authorization.vulnerable import vulnerable_schema
        return vulnerable_schema
    from scenarios.alias_authorization.hardened import hardened_schema
    return hardened_schema


async def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    schema = _get_schema(config.mode)
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.monotonic()

    result = schema.execute_sync(ALIASED_QUERY_SNAKE, context_value=ALICE_CTX)
    duration_ms = int((time.monotonic() - t0) * 1000)
    completed = datetime.now(timezone.utc).isoformat()

    data = result.data or {}
    errors = result.errors or []

    my_order = data.get("myOrder")
    bobs_order = data.get("bobsOrder")

    evidence_items = [
        Evidence(
            type="order_access",
            label="Alice's Own Order (id=1)",
            data={
                "order_id": "1",
                "expected_owner": "1",
                "actually_returned": my_order is not None,
                "authorized": True,
                "data": my_order,
            },
            timestamp=completed,
        ),
        Evidence(
            type="order_access",
            label="Bob's Order via Alias (id=3)",
            data={
                "order_id": "3",
                "expected_owner": "2",
                "actually_returned": bobs_order is not None,
                "authorized": False,
                "idor_flaw_triggered": bobs_order is not None,
                "errors": [str(e) for e in errors],
            },
            timestamp=completed,
        ),
    ]

    flaw_triggered = bobs_order is not None
    if config.mode == LabMode.VULNERABLE:
        actual_outcome = (
            "IDOR: Alice retrieved Bob's order via alias — both orders returned"
            if flaw_triggered else "Unexpectedly blocked"
        )
    else:
        actual_outcome = (
            "Defense active: cross-user order blocked with PermissionError"
            if not flaw_triggered else "Defense FAILED — cross-user order still accessible"
        )

    return ExperimentResult(
        id=str(uuid.uuid4()),
        scenario_id=ScenarioId.ALIAS_AUTHORIZATION,
        mode=config.mode,
        config=config.parameters,
        status=ExperimentStatus.COMPLETED,
        started_at=started,
        completed_at=completed,
        duration_ms=duration_ms,
        input_summary="Aliased query as Alice requesting own order + Bob's order",
        expected_outcome=(
            "Both orders returned (IDOR)" if config.mode == LabMode.VULNERABLE
            else "Bob's order blocked by ownership check"
        ),
        actual_outcome=actual_outcome,
        evidence=evidence_items,
        is_sample=True,
    )


async def verify_defense(mode: LabMode) -> DefenseResult:
    schema = _get_schema(mode)
    result = schema.execute_sync(ALIASED_QUERY_SNAKE, context_value=ALICE_CTX)
    data = result.data or {}
    bobs_order = data.get("bobsOrder")
    blocked = bobs_order is None
    return DefenseResult(
        control_id="alias-idor-ownership-check",
        verified=blocked if mode == LabMode.HARDENED else not blocked,
        description="Cross-user order access blocked via ownership enforcement",
        details={
            "bobs_order_returned": bobs_order,
            "errors": [str(e) for e in (result.errors or [])],
        },
    )
