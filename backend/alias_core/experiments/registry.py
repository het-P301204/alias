"""Scenario registry — holds all registered ScenarioModule instances."""
from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

from alias_core.experiments.models import ScenarioId

if TYPE_CHECKING:
    from scenarios.base import ScenarioModule


class ScenarioRegistry:
    def __init__(self) -> None:
        self._modules: dict[str, "ScenarioModule"] = {}

    def register(self, module: "ScenarioModule") -> None:
        self._modules[module.scenario_id] = module

    def get(self, scenario_id: str) -> "ScenarioModule":
        if scenario_id not in self._modules:
            raise KeyError(f"Unknown scenario: {scenario_id!r}")
        return self._modules[scenario_id]

    def all(self) -> list["ScenarioModule"]:
        return list(self._modules.values())

    def ids(self) -> list[str]:
        return list(self._modules.keys())

    def discover(self) -> None:
        """Auto-discover and import scenario packages from the scenarios/ directory."""
        try:
            import scenarios as _scenarios_pkg
        except ImportError:
            return

        for finder, name, _ispkg in pkgutil.iter_modules(_scenarios_pkg.__path__):
            module_path = f"scenarios.{name}"
            try:
                mod = importlib.import_module(module_path)
            except Exception:
                continue

            # Each scenario package exposes a module-level `scenario` instance.
            scenario_instance = getattr(mod, "scenario", None)
            if scenario_instance is not None and hasattr(scenario_instance, "scenario_id"):
                self.register(scenario_instance)


registry = ScenarioRegistry()
