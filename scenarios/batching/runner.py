import time
import uuid
from datetime import datetime, timezone

from alias_core.experiments.models import (
    ExperimentConfig, ExperimentResult, ExperimentStatus,
    Evidence, DefenseResult, LabMode,
)
from alias_core.experiments.models import ScenarioId
from scenarios.batching.fixtures import DEMO_ACCOUNTS, DEMO_PASSWORDS


def _build_batch_query(accounts: list[tuple[str, str]]) -> str:
    aliases = []
    for i, (username, password) in enumerate(accounts):
        aliases.append(
            f'  op{i}: authenticateUser(username: "{username}", password: "{password}") '
            f'{{ success token userId }}'
        )
    return "mutation {\n" + "\n".join(aliases) + "\n}"


def _get_schema(mode: LabMode):
    if mode == LabMode.VULNERABLE:
        from scenarios.batching.vulnerable import vulnerable_schema
        return vulnerable_schema
    from scenarios.batching.hardened import hardened_schema
    return hardened_schema


async def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    schema = _get_schema(config.mode)
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.monotonic()

    test_creds = list(DEMO_PASSWORDS.items())  # 5 pairs
    batch_query = _build_batch_query(test_creds)

    result = schema.execute_sync(batch_query, context_value={})
    duration_ms = int((time.monotonic() - t0) * 1000)
    completed = datetime.now(timezone.utc).isoformat()

    errors = result.errors or []
    data = result.data or {}

    rate_limit_triggered = bool(errors)
    ops_accepted = len([k for k in data if data[k] is not None]) if data else 0
    ops_attempted = len(test_creds)
    ops_rejected = ops_attempted - ops_accepted if not rate_limit_triggered else ops_attempted

    if rate_limit_triggered:
        ops_accepted = 0
        ops_rejected = ops_attempted

    evidence = [
        Evidence(
            type="batch_auth_result",
            label="Batch Authentication Attempt",
            data={
                "http_requests": 1,
                "operations_attempted": ops_attempted,
                "operations_accepted": ops_accepted,
                "rejected": ops_rejected,
                "rate_limit_triggered": rate_limit_triggered,
                "errors": [str(e) for e in errors],
                "results": {k: v for k, v in data.items()},
            },
            timestamp=completed,
        )
    ]

    if config.mode == LabMode.VULNERABLE:
        actual_outcome = f"All {ops_attempted} auth operations executed in 1 HTTP request"
    else:
        actual_outcome = (
            f"Batch blocked after limit: {ops_accepted} accepted, {ops_rejected} rejected"
            if rate_limit_triggered
            else "Defense did not trigger as expected"
        )

    return ExperimentResult(
        id=str(uuid.uuid4()),
        scenario_id=ScenarioId.BATCHING,
        mode=config.mode,
        config=config.parameters,
        status=ExperimentStatus.COMPLETED,
        started_at=started,
        completed_at=completed,
        duration_ms=duration_ms,
        input_summary=f"1 HTTP request with {ops_attempted} aliased authenticateUser mutations",
        expected_outcome=(
            "All 5 operations execute (no GraphQL-layer limit)"
            if config.mode == LabMode.VULNERABLE
            else f"Batch rejected: exceeds max {3} operations per request"
        ),
        actual_outcome=actual_outcome,
        evidence=evidence,
        is_sample=True,
    )


async def verify_defense(mode: LabMode) -> DefenseResult:
    schema = _get_schema(mode)
    creds = list(DEMO_PASSWORDS.items())
    query = _build_batch_query(creds)
    result = schema.execute_sync(query, context_value={})
    blocked = bool(result.errors)
    return DefenseResult(
        control_id="batch-operation-limit",
        verified=blocked if mode == LabMode.HARDENED else not blocked,
        description=f"5-operation batch blocked at GraphQL layer (limit=3) in hardened mode",
        details={"errors": [str(e) for e in (result.errors or [])], "data": result.data},
    )
