"""Real assertion tests for the query-complexity scenario."""
import asyncio

from alias_core.experiments.models import ExperimentConfig, LabMode, ScenarioId
from scenarios.query_complexity import scenario
from scenarios.query_complexity.runner import calculate_depth, estimate_complexity


# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------

def test_shallow_query_depth():
    query = "{ users { id name } }"
    assert calculate_depth(query) == 2


def test_deep_query_depth():
    query = "{ users { posts { comments { author { id } } } } }"
    assert calculate_depth(query) == 5


def test_single_field_depth():
    assert calculate_depth("{ users { id } }") == 2


def test_complexity_grows_with_nesting():
    shallow = estimate_complexity("{ users { id } }", list_multiplier=3)
    deep = estimate_complexity(
        "{ users { posts { comments { author { id } } } } }",
        list_multiplier=3,
    )
    assert deep > shallow * 5, f"deep={deep}, shallow={shallow}"


def test_complexity_default_multiplier_is_1():
    c = estimate_complexity("{ users { id } }")
    assert c >= 1


def test_complexity_multiplier_increases_score():
    base = estimate_complexity("{ users { id } }", list_multiplier=1)
    high = estimate_complexity("{ users { id } }", list_multiplier=10)
    assert high > base


# ---------------------------------------------------------------------------
# Scenario integration tests
# ---------------------------------------------------------------------------

def test_metadata_id():
    meta = scenario.get_metadata()
    assert meta.id == ScenarioId.QUERY_COMPLEXITY


def test_metadata_has_objectives():
    meta = scenario.get_metadata()
    assert len(meta.learning_objectives) >= 3


def test_vulnerable_run_completes():
    config = ExperimentConfig(scenario_id=ScenarioId.QUERY_COMPLEXITY, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.status.value == "completed"


def test_vulnerable_allows_deep_query():
    """In vulnerable mode, the deep query (depth=5) is not rejected."""
    config = ExperimentConfig(scenario_id=ScenarioId.QUERY_COMPLEXITY, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    deep_results = [e for e in result.evidence if e.data.get("query_label") == "deep"]
    assert len(deep_results) > 0, "Must have deep query evidence"
    assert deep_results[0].data.get("rejected") is False, "Deep query must not be rejected in vulnerable mode"


def test_vulnerable_allows_shallow_query():
    config = ExperimentConfig(scenario_id=ScenarioId.QUERY_COMPLEXITY, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    shallow_results = [e for e in result.evidence if e.data.get("query_label") == "shallow"]
    assert len(shallow_results) > 0
    assert shallow_results[0].data.get("rejected") is False


def test_hardened_run_completes():
    config = ExperimentConfig(scenario_id=ScenarioId.QUERY_COMPLEXITY, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.status.value == "completed"


def test_hardened_rejects_deep_query():
    """In hardened mode, the deep query (depth=5) is rejected by the depth limit (max=4)."""
    config = ExperimentConfig(scenario_id=ScenarioId.QUERY_COMPLEXITY, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    deep_results = [e for e in result.evidence if e.data.get("query_label") == "deep"]
    assert len(deep_results) > 0, "Must have deep query evidence"
    assert deep_results[0].data.get("rejected") is True, "Deep query must be rejected in hardened mode"


def test_hardened_allows_shallow_query():
    config = ExperimentConfig(scenario_id=ScenarioId.QUERY_COMPLEXITY, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    shallow_results = [e for e in result.evidence if e.data.get("query_label") == "shallow"]
    assert len(shallow_results) > 0
    assert shallow_results[0].data.get("rejected") is False


def test_hardened_verify_defense():
    defense = asyncio.run(scenario.verify_defense(LabMode.HARDENED))
    assert defense.verified is True


def test_result_has_evidence_for_both_queries():
    config = ExperimentConfig(scenario_id=ScenarioId.QUERY_COMPLEXITY, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    labels = {e.data.get("query_label") for e in result.evidence}
    assert "shallow" in labels
    assert "deep" in labels
