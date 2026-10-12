import time
import uuid
from datetime import datetime, timezone

from alias_core.experiments.models import (
    ExperimentConfig, ExperimentResult, ExperimentStatus,
    Evidence, DefenseResult, LabMode,
)
from alias_core.experiments.models import ScenarioId
from scenarios.blind_recovery.fixtures import PROBE_ID

# Two non-existent IDs to run distinct probes
PROBE_QUERY_1 = f'{{ user(id: "{PROBE_ID}") {{ id username email }} }}'
PROBE_QUERY_2 = '{ user(id: "u8888") { id username email } }'

PROBES = [
    ("non_existent_user_1", PROBE_QUERY_1),
    ("non_existent_user_2", PROBE_QUERY_2),
]


def _get_schema(mode: LabMode):
    if mode == LabMode.VULNERABLE:
        from scenarios.blind_recovery.vulnerable import vulnerable_schema
        return vulnerable_schema
    from scenarios.blind_recovery.hardened import hardened_schema
    return hardened_schema


def _error_reveals_suggestion(msg: str) -> bool:
    msg_lower = msg.lower()
    return (
        "did you mean" in msg_lower
        or "valid ids" in msg_lower
        or "not found in" in msg_lower
        or "keys" in msg_lower
    )


async def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    schema = _get_schema(config.mode)
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.monotonic()

    evidence: list[Evidence] = []

    for probe_name, query in PROBES:
        result = schema.execute_sync(query, context_value={})
        errors = result.errors or []

        if errors:
            # Error(s) present — check if they reveal schema hints
            for err in errors:
                msg = str(getattr(err, "message", err))
                reveals = _error_reveals_suggestion(msg)
                evidence.append(Evidence(
                    type="error_analysis",
                    label=f"Probe: {probe_name} (error returned)",
                    data={
                        "probe": probe_name,
                        "query": query,
                        "error_message": msg,
                        "reveals_suggestion": reveals,
                        "result_data": result.data,
                    },
                    timestamp=started,
                ))
        else:
            # No error — null returned (hardened mode defense)
            evidence.append(Evidence(
                type="error_analysis",
                label=f"Probe: {probe_name} (null returned — no error)",
                data={
                    "probe": probe_name,
                    "query": query,
                    "error_message": None,
                    "reveals_suggestion": False,
                    "result_data": result.data,
                    "note": "Null returned instead of a revealing error message",
                },
                timestamp=started,
            ))

    duration_ms = int((time.monotonic() - t0) * 1000)
    completed = datetime.now(timezone.utc).isoformat()

    any_reveals = any(e.data.get("reveals_suggestion") for e in evidence)

    if config.mode == LabMode.VULNERABLE:
        actual_outcome = (
            "Error messages reveal internal schema hints (valid IDs, field names)"
            if any_reveals else "No schema hints leaked (unexpected for vulnerable mode)"
        )
    else:
        actual_outcome = (
            "Null returned — no error message leaks schema structure"
            if not any_reveals else "Defense failed — error messages still contain hints"
        )

    return ExperimentResult(
        id=str(uuid.uuid4()),
        scenario_id=ScenarioId.BLIND_RECOVERY,
        mode=config.mode,
        config=config.parameters,
        status=ExperimentStatus.COMPLETED,
        started_at=started,
        completed_at=completed,
        duration_ms=duration_ms,
        input_summary="Two non-existent entity probes to observe error message verbosity",
        expected_outcome=(
            "Verbose errors reveal valid IDs and internal details"
            if config.mode == LabMode.VULNERABLE
            else "Null returned — no revealing error messages"
        ),
        actual_outcome=actual_outcome,
        evidence=evidence,
        is_sample=True,
    )


async def verify_defense(mode: LabMode) -> DefenseResult:
    schema = _get_schema(mode)
    result = schema.execute_sync(PROBE_QUERY_1, context_value={})
    errors = result.errors or []

    reveals_any = any(
        _error_reveals_suggestion(str(getattr(e, "message", e)))
        for e in errors
    )

    if mode == LabMode.HARDENED:
        verified = not reveals_any
    else:
        verified = reveals_any

    return DefenseResult(
        control_id="error-message-sanitization",
        verified=verified,
        description="Non-existent entity returns null without a revealing error in hardened mode",
        details={
            "errors": [str(getattr(e, "message", e)) for e in errors],
            "reveals_suggestion": reveals_any,
            "null_returned": result.data is not None and not errors,
        },
    )
