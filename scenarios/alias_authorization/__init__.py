import strawberry

from alias_core.experiments.models import (
    ExperimentConfig, ExperimentResult, DefenseResult, LabMode, ScenarioMetadata,
)
from alias_core.experiments.models import ScenarioId
from scenarios.alias_authorization import runner as _runner
from scenarios.alias_authorization.fixtures import reset_fixtures


class AliasAuthorizationScenario:
    scenario_id = ScenarioId.ALIAS_AUTHORIZATION

    def get_metadata(self) -> ScenarioMetadata:
        return ScenarioMetadata(
            id=ScenarioId.ALIAS_AUTHORIZATION,
            title="Alias-Based Authorization Bypass (IDOR)",
            description=(
                "Shows how GraphQL aliases let an attacker request another user's "
                "resources in a single query when resolvers omit ownership checks."
            ),
            category="Broken Object Level Authorization",
            difficulty="intermediate",
            learning_objectives=[
                "Understand GraphQL field aliasing mechanics",
                "Reproduce an IDOR via aliased queries",
                "Implement and verify per-resolver ownership checks",
            ],
        )

    def get_schema(self, mode: LabMode) -> strawberry.Schema:
        if mode == LabMode.VULNERABLE:
            from scenarios.alias_authorization.vulnerable import vulnerable_schema
            return vulnerable_schema
        from scenarios.alias_authorization.hardened import hardened_schema
        return hardened_schema

    async def run_experiment(self, config: ExperimentConfig) -> ExperimentResult:
        return await _runner.run_experiment(config)

    async def verify_defense(self, mode: LabMode) -> DefenseResult:
        return await _runner.verify_defense(mode)

    async def reset(self) -> None:
        reset_fixtures()


scenario = AliasAuthorizationScenario()
