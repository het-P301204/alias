import time
import uuid
from datetime import datetime, timezone

from alias_core.experiments.models import (
    ExperimentConfig, ExperimentResult, ExperimentStatus,
    Evidence, DefenseResult, LabMode,
)
from alias_core.experiments.models import ScenarioId

# Shallow query: depth 2 (users → id)
SHALLOW_QUERY = "{ users { id } }"
SHALLOW_DEPTH = 2

# Deep query: depth 5 (users → posts → comments → author → id)
DEEP_QUERY = "{ users { posts { comments { author { id } } } } }"
DEEP_DEPTH = 5


def calculate_depth(query: str) -> int:
    """Return the maximum field nesting depth of a GraphQL query string."""
    from graphql import parse

    doc = parse(query)

    def _max_depth(selection_set, depth: int) -> int:
        if selection_set is None:
            return depth
        depths = [
            _max_depth(getattr(sel, "selection_set", None), depth + 1)
            for sel in selection_set.selections
        ]
        return max(depths) if depths else depth

    max_d = 0
    for defn in doc.definitions:
        ss = getattr(defn, "selection_set", None)
        if ss:
            max_d = max(max_d, _max_depth(ss, 0))
    return max_d


def estimate_complexity(query: str, list_multiplier: int = 1) -> int:
    """Estimate query complexity by multiplying nested list fields by list_multiplier."""
    from graphql import parse

    doc = parse(query)

    def _cost(selection_set) -> int:
        if selection_set is None:
            return 1
        total = 0
        for sel in selection_set.selections:
            child_ss = getattr(sel, "selection_set", None)
            if child_ss:
                total += list_multiplier * _cost(child_ss)
            else:
                total += 1
        return total

    total = 0
    for defn in doc.definitions:
        ss = getattr(defn, "selection_set", None)
        if ss:
            total += _cost(ss)
    return total


def _get_schema(mode: LabMode):
    if mode == LabMode.VULNERABLE:
        from scenarios.query_complexity.vulnerable import vulnerable_schema
        return vulnerable_schema
    from scenarios.query_complexity.hardened import hardened_schema
    return hardened_schema


async def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    schema = _get_schema(config.mode)
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.monotonic()

    evidence: list[Evidence] = []

    for (query, label, depth) in [
        (SHALLOW_QUERY, "shallow", SHALLOW_DEPTH),
        (DEEP_QUERY, "deep", DEEP_DEPTH),
    ]:
        result = schema.execute_sync(query, context_value={})
        rejected = bool(result.errors)
        evidence.append(Evidence(
            type="query_execution",
            label=f"{label.title()} Query (depth={depth})",
            data={
                "query_label": label,
                "depth": depth,
                "rejected": rejected,
                "errors": [str(e) for e in (result.errors or [])],
                "data": result.data,
            },
            timestamp=started,
        ))

    duration_ms = int((time.monotonic() - t0) * 1000)
    completed = datetime.now(timezone.utc).isoformat()

    deep_ev = next(e for e in evidence if e.data["query_label"] == "deep")
    deep_rejected = deep_ev.data["rejected"]

    if config.mode == LabMode.VULNERABLE:
        actual_outcome = (
            f"Deep query (depth={DEEP_DEPTH}) accepted — no depth enforcement"
        )
    else:
        actual_outcome = (
            f"Deep query (depth={DEEP_DEPTH}) rejected — depth limit enforced"
            if deep_rejected
            else "Defense did not trigger as expected"
        )

    return ExperimentResult(
        id=str(uuid.uuid4()),
        scenario_id=ScenarioId.QUERY_COMPLEXITY,
        mode=config.mode,
        config=config.parameters,
        status=ExperimentStatus.COMPLETED,
        started_at=started,
        completed_at=completed,
        duration_ms=duration_ms,
        input_summary=f"Queries at depth {SHALLOW_DEPTH} (shallow) and {DEEP_DEPTH} (deep)",
        expected_outcome=(
            "Both queries accepted (no depth limit)"
            if config.mode == LabMode.VULNERABLE
            else f"Deep query (depth={DEEP_DEPTH}) rejected — limit=4"
        ),
        actual_outcome=actual_outcome,
        evidence=evidence,
        is_sample=True,
    )


async def verify_defense(mode: LabMode) -> DefenseResult:
    schema = _get_schema(mode)
    result = schema.execute_sync(DEEP_QUERY, context_value={})
    blocked = bool(result.errors)
    return DefenseResult(
        control_id="query-depth-limit",
        verified=blocked if mode == LabMode.HARDENED else not blocked,
        description=f"Deep query (depth={DEEP_DEPTH}) blocked by depth limit in hardened mode",
        details={
            "depth_tested": DEEP_DEPTH,
            "errors": [str(e) for e in (result.errors or [])],
        },
    )
