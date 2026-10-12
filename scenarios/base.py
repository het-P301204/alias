"""Scenario protocol — every scenario package must expose a `scenario` instance implementing this."""
from typing import Protocol, runtime_checkable

import strawberry

from alias_core.experiments.models import (
    ExperimentConfig,
    ExperimentResult,
    DefenseResult,
    ScenarioMetadata,
    LabMode,
)


@runtime_checkable
class ScenarioModule(Protocol):
    scenario_id: str

    def get_metadata(self) -> ScenarioMetadata: ...
    def get_schema(self, mode: LabMode) -> strawberry.Schema: ...
    async def run_experiment(self, config: ExperimentConfig) -> ExperimentResult: ...
    async def verify_defense(self, mode: LabMode) -> DefenseResult: ...
    async def reset(self) -> None: ...
