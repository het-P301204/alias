import time
import uuid
from datetime import datetime, timezone

from alias_core.experiments.models import (
    ExperimentConfig, ExperimentResult, ExperimentStatus,
    Evidence, DefenseResult, LabMode,
)
from alias_core.experiments.models import ScenarioId

INTROSPECTION_QUERY = """
{
  __schema {
    queryType { name }
    mutationType { name }
    types {
      name
      kind
      fields {
        name
        isDeprecated
        deprecationReason
        args { name type { name kind } }
      }
    }
  }
}
"""


def _get_schema(mode: LabMode):
    if mode == LabMode.VULNERABLE:
        from scenarios.introspection.vulnerable import vulnerable_schema
        return vulnerable_schema
    from scenarios.introspection.hardened import hardened_schema
    return hardened_schema


async def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    schema = _get_schema(config.mode)
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.monotonic()

    result = schema.execute_sync(INTROSPECTION_QUERY, context_value={})
    duration_ms = int((time.monotonic() - t0) * 1000)
    completed = datetime.now(timezone.utc).isoformat()

    evidence: list[Evidence] = []
    status = ExperimentStatus.COMPLETED
    actual_outcome = ""

    if result.errors:
        err_msgs = [str(e) for e in result.errors]
        actual_outcome = f"Introspection blocked: {err_msgs[0]}"
        evidence.append(Evidence(
            type="introspection_blocked",
            label="Introspection Rejected",
            data={"errors": err_msgs},
            timestamp=completed,
        ))
    else:
        schema_data = (result.data or {}).get("__schema", {})
        types = schema_data.get("types", [])
        user_types = [t for t in types if t and not (t.get("name") or "").startswith("__")]
        mutations = schema_data.get("mutationType", {})
        deprecated_fields = []
        for t in user_types:
            for f in (t.get("fields") or []):
                if f and f.get("isDeprecated"):
                    deprecated_fields.append(f"{t['name']}.{f['name']}")

        actual_outcome = (
            f"Schema exposed: {len(user_types)} types, "
            f"{len(deprecated_fields)} deprecated fields"
        )
        evidence.append(Evidence(
            type="schema_dump",
            label="Schema Fully Exposed",
            data={
                "type_count": len(user_types),
                "types": [t.get("name") for t in user_types],
                "mutations_exposed": mutations.get("name") is not None,
                "deprecated_fields": deprecated_fields,
            },
            timestamp=completed,
        ))

    return ExperimentResult(
        id=str(uuid.uuid4()),
        scenario_id=ScenarioId.INTROSPECTION,
        mode=config.mode,
        config=config.parameters,
        status=status,
        started_at=started,
        completed_at=completed,
        duration_ms=duration_ms,
        input_summary="GraphQL introspection query (__schema)",
        expected_outcome=(
            "Full schema disclosure" if config.mode == LabMode.VULNERABLE
            else "Introspection disabled error"
        ),
        actual_outcome=actual_outcome,
        evidence=evidence,
        is_sample=True,
    )


async def verify_defense(mode: LabMode) -> DefenseResult:
    schema = _get_schema(mode)
    result = schema.execute_sync(INTROSPECTION_QUERY, context_value={})
    blocked = bool(result.errors)
    return DefenseResult(
        control_id="introspection-disabled",
        verified=blocked if mode == LabMode.HARDENED else not blocked,
        description="__schema query is rejected in hardened mode",
        details={"errors": [str(e) for e in (result.errors or [])]},
    )
