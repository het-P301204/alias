import strawberry

from alias_core.experiments.models import (
    ExperimentConfig, ExperimentResult, DefenseResult, LabMode, ScenarioMetadata,
)
from alias_core.experiments.models import ScenarioId
from scenarios.query_complexity import runner as _runner


class QueryComplexityScenario:
    scenario_id = ScenarioId.QUERY_COMPLEXITY

    def get_metadata(self) -> ScenarioMetadata:
        return ScenarioMetadata(
            id=ScenarioId.QUERY_COMPLEXITY,
            title="Query Depth & Complexity Attack",
            description=(
                "Demonstrates how deeply-nested GraphQL queries can exhaust server "
                "CPU and memory when no depth or complexity limits are enforced."
            ),
            category="Denial of Service",
            difficulty="intermediate",
            learning_objectives=[
                "Understand how query depth multiplies resolver invocations",
                "Calculate query complexity scores for nested queries",
                "Implement DepthLimitExtension to cap query depth at the schema level",
            ],
        )

    def get_schema(self, mode: LabMode) -> strawberry.Schema:
        if mode == LabMode.VULNERABLE:
            from scenarios.query_complexity.vulnerable import vulnerable_schema
            return vulnerable_schema
        from scenarios.query_complexity.hardened import hardened_schema
        return hardened_schema

    async def run_experiment(self, config: ExperimentConfig) -> ExperimentResult:
        return await _runner.run_experiment(config)

    async def verify_defense(self, mode: LabMode) -> DefenseResult:
        return await _runner.verify_defense(mode)

    async def reset(self) -> None:
        pass


scenario = QueryComplexityScenario()
