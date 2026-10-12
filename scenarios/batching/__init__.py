import strawberry

from alias_core.experiments.models import (
    ExperimentConfig, ExperimentResult, DefenseResult, LabMode, ScenarioMetadata,
)
from alias_core.experiments.models import ScenarioId
from scenarios.batching import runner as _runner


class BatchingScenario:
    scenario_id = ScenarioId.BATCHING

    def get_metadata(self) -> ScenarioMetadata:
        return ScenarioMetadata(
            id=ScenarioId.BATCHING,
            title="GraphQL Batching Abuse",
            description=(
                "Demonstrates how GraphQL aliases allow an attacker to pack many "
                "auth operations into a single HTTP request, bypassing HTTP-level "
                "rate limiting while exhausting server resources."
            ),
            category="Rate Limiting / DoS",
            difficulty="intermediate",
            learning_objectives=[
                "Understand how GraphQL aliases bypass HTTP rate limits",
                "Measure per-request operation counts",
                "Implement an OperationLimitExtension to cap batch size",
            ],
        )

    def get_schema(self, mode: LabMode) -> strawberry.Schema:
        if mode == LabMode.VULNERABLE:
            from scenarios.batching.vulnerable import vulnerable_schema
            return vulnerable_schema
        from scenarios.batching.hardened import hardened_schema
        return hardened_schema

    async def run_experiment(self, config: ExperimentConfig) -> ExperimentResult:
        return await _runner.run_experiment(config)

    async def verify_defense(self, mode: LabMode) -> DefenseResult:
        return await _runner.verify_defense(mode)

    async def reset(self) -> None:
        pass


scenario = BatchingScenario()
