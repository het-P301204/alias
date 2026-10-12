"""ALIAS CLI — Typer + Rich interface for the GraphQL security research platform."""
from __future__ import annotations

import asyncio
import importlib
import json
import socket
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import box

app = typer.Typer(
    name="alias",
    help="ALIAS — GraphQL Security Research Platform CLI",
    no_args_is_help=True,
)
lab_app = typer.Typer(help="Manage lab scenarios")
test_app = typer.Typer(help="Run scenario experiments")
report_app = typer.Typer(help="List and export experiment reports")

app.add_typer(lab_app, name="lab")
app.add_typer(test_app, name="test")
app.add_typer(report_app, name="report")

console = Console()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_import(name: str) -> bool:
    try:
        importlib.import_module(name)
        return True
    except ImportError:
        return False


def _check_db() -> bool:
    try:
        from alias_core.config.settings import settings
        from pathlib import Path
        db_path = Path(settings.db_path)
        if db_path.exists():
            return True
        # Try creating it
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def _check_port(port: int) -> bool:
    """Return True if the port is free (not in use)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def _status_mark(ok: bool) -> str:
    return "[green]✓[/green]" if ok else "[red]✗[/red]"


# ---------------------------------------------------------------------------
# alias doctor
# ---------------------------------------------------------------------------

@app.command()
def doctor() -> None:
    """Check environment readiness: Python version, dependencies, DB, and port."""
    checks = [
        ("Python >= 3.12", sys.version_info >= (3, 12)),
        ("typer installed", _check_import("typer")),
        ("rich installed", _check_import("rich")),
        ("strawberry-graphql installed", _check_import("strawberry")),
        ("fastapi installed", _check_import("fastapi")),
        ("aiosqlite installed", _check_import("aiosqlite")),
        ("uvicorn installed", _check_import("uvicorn")),
        ("Database path accessible", _check_db()),
        ("Backend port 8000 free", _check_port(8000)),
    ]

    table = Table(title="ALIAS Environment Check", box=box.ROUNDED)
    table.add_column("Check", style="bold")
    table.add_column("Status", justify="center")

    all_ok = True
    for label, ok in checks:
        table.add_row(label, _status_mark(ok))
        if not ok:
            all_ok = False

    console.print(table)

    if all_ok:
        console.print("\n[green bold]All checks passed — ready to run ALIAS.[/green bold]")
    else:
        console.print("\n[yellow]Some checks failed. Fix the issues above before starting.[/yellow]")
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# alias lab list
# ---------------------------------------------------------------------------

@lab_app.command("list")
def lab_list() -> None:
    """List all available scenarios with metadata."""
    from alias_core.experiments.registry import registry
    registry.discover()

    table = Table(title="ALIAS Scenarios", box=box.ROUNDED)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="bold")
    table.add_column("Category")
    table.add_column("Difficulty")

    for mod in sorted(registry.all(), key=lambda m: str(m.scenario_id)):
        meta = mod.get_metadata()
        diff_color = {
            "beginner": "green",
            "intermediate": "yellow",
            "advanced": "red",
        }.get(meta.difficulty, "white")
        table.add_row(
            str(meta.id.value),
            meta.title,
            meta.category,
            f"[{diff_color}]{meta.difficulty}[/{diff_color}]",
        )

    console.print(table)


# ---------------------------------------------------------------------------
# alias lab start
# ---------------------------------------------------------------------------

@lab_app.command("start")
def lab_start(
    host: str = typer.Option("127.0.0.1", help="Bind address"),
    port: int = typer.Option(8000, help="Listen port"),
    reload: bool = typer.Option(False, "--reload", help="Enable hot reload"),
) -> None:
    """Start the ALIAS backend server (uvicorn)."""
    console.print(f"[bold green]Starting ALIAS server on {host}:{port}…[/bold green]")
    cmd = [
        sys.executable, "-m", "uvicorn",
        "alias_core.api.main:app",
        "--host", host,
        "--port", str(port),
    ]
    if reload:
        cmd.append("--reload")
    subprocess.run(cmd, check=False)


# ---------------------------------------------------------------------------
# alias test run
# ---------------------------------------------------------------------------

@test_app.command("run")
def test_run(
    scenario: str = typer.Option(..., "--scenario", "-s", help="Scenario ID"),
    mode: str = typer.Option("vulnerable", "--mode", "-m", help="Lab mode: vulnerable|hardened"),
    output_json: bool = typer.Option(False, "--json", help="Output raw JSON to stdout"),
) -> None:
    """Run a scenario experiment and display the results."""
    from alias_core.experiments.models import ExperimentConfig, LabMode, ScenarioId
    from alias_core.experiments.registry import registry
    registry.discover()

    try:
        scenario_id = ScenarioId(scenario)
    except ValueError:
        console.print(f"[red]Unknown scenario: {scenario!r}[/red]")
        valid = [e.value for e in ScenarioId]
        console.print(f"Valid IDs: {', '.join(valid)}")
        raise typer.Exit(code=1)

    try:
        lab_mode = LabMode(mode)
    except ValueError:
        console.print(f"[red]Invalid mode: {mode!r}. Use 'vulnerable' or 'hardened'.[/red]")
        raise typer.Exit(code=1)

    try:
        mod = registry.get(scenario_id.value)
    except KeyError:
        console.print(f"[red]Scenario {scenario_id.value!r} is not registered. Run 'alias lab list' to see available scenarios.[/red]")
        raise typer.Exit(code=1)

    config = ExperimentConfig(scenario_id=scenario_id, mode=lab_mode, parameters={})

    console.print(f"Running [bold]{scenario_id.value}[/bold] in [yellow]{lab_mode.value}[/yellow] mode…")

    result = asyncio.run(mod.run_experiment(config))

    if output_json:
        print(result.model_dump_json(indent=2))
        return

    # Rich summary table
    table = Table(title=f"Result: {scenario_id.value} ({lab_mode.value})", box=box.ROUNDED)
    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("Status", f"[green]{result.status.value}[/green]" if result.status.value == "completed" else f"[red]{result.status.value}[/red]")
    table.add_row("Duration", f"{result.duration_ms or 0} ms")
    table.add_row("Expected", result.expected_outcome or "—")
    table.add_row("Observed", result.actual_outcome or "—")
    table.add_row("Evidence items", str(len(result.evidence)))

    if result.defensive_control_result:
        d = result.defensive_control_result
        verified_str = "[green]Verified[/green]" if d.verified else "[red]Not verified[/red]"
        table.add_row("Defense control", f"{d.control_id} — {verified_str}")

    if result.error:
        table.add_row("Error", f"[red]{result.error}[/red]")

    console.print(table)


# ---------------------------------------------------------------------------
# alias test compare
# ---------------------------------------------------------------------------

@test_app.command("compare")
def test_compare(
    scenario: str = typer.Option(..., "--scenario", "-s", help="Scenario ID"),
) -> None:
    """Run both vulnerable and hardened modes and compare side by side."""
    from alias_core.experiments.models import ExperimentConfig, LabMode, ScenarioId
    from alias_core.experiments.registry import registry
    registry.discover()

    try:
        scenario_id = ScenarioId(scenario)
    except ValueError:
        console.print(f"[red]Unknown scenario: {scenario!r}[/red]")
        raise typer.Exit(code=1)

    try:
        mod = registry.get(scenario_id.value)
    except KeyError:
        console.print(f"[red]Scenario {scenario_id.value!r} not registered.[/red]")
        raise typer.Exit(code=1)

    results = {}
    for mode in (LabMode.VULNERABLE, LabMode.HARDENED):
        config = ExperimentConfig(scenario_id=scenario_id, mode=mode, parameters={})
        console.print(f"Running [yellow]{mode.value}[/yellow]…")
        results[mode] = asyncio.run(mod.run_experiment(config))

    table = Table(title=f"Comparison: {scenario_id.value}", box=box.ROUNDED)
    table.add_column("Field", style="bold")
    table.add_column("Vulnerable", style="red")
    table.add_column("Hardened", style="green")

    table.add_row(
        "Status",
        results[LabMode.VULNERABLE].status.value,
        results[LabMode.HARDENED].status.value,
    )
    table.add_row(
        "Outcome",
        results[LabMode.VULNERABLE].actual_outcome or "—",
        results[LabMode.HARDENED].actual_outcome or "—",
    )
    table.add_row(
        "Evidence items",
        str(len(results[LabMode.VULNERABLE].evidence)),
        str(len(results[LabMode.HARDENED].evidence)),
    )

    console.print(table)


# ---------------------------------------------------------------------------
# alias report list
# ---------------------------------------------------------------------------

@report_app.command("list")
def report_list(
    limit: int = typer.Option(10, "--limit", "-n", help="Max rows to show"),
) -> None:
    """List recent experiments."""
    from alias_core.database.init_db import get_db
    from alias_core.database.queries import list_experiments

    async def _fetch():
        async with get_db() as db:
            return await list_experiments(db, page=1, limit=limit)

    items, total = asyncio.run(_fetch())

    table = Table(title=f"Recent Experiments (showing {len(items)} of {total})", box=box.ROUNDED)
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Scenario", style="cyan")
    table.add_column("Mode")
    table.add_column("Status")
    table.add_column("Started")

    for exp in items:
        mode_style = "red" if exp.mode.value == "vulnerable" else "green"
        table.add_row(
            exp.id[:8] + "…",
            exp.scenario_id.value,
            f"[{mode_style}]{exp.mode.value}[/{mode_style}]",
            exp.status.value,
            (exp.started_at or "")[:19],
        )

    console.print(table)


# ---------------------------------------------------------------------------
# alias report export
# ---------------------------------------------------------------------------

@report_app.command("export")
def report_export(
    exp_id: str = typer.Option(..., "--id", help="Experiment UUID"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json|csv|html"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Export an experiment report to JSON, CSV, or HTML."""
    if format not in ("json", "csv", "html"):
        console.print("[red]Format must be json, csv, or html.[/red]")
        raise typer.Exit(code=1)

    from alias_core.database.init_db import get_db
    from alias_core.database.queries import get_experiment
    from alias_core.reporting.generator import generate_json, generate_csv, generate_html

    async def _fetch():
        async with get_db() as db:
            return await get_experiment(db, exp_id)

    result = asyncio.run(_fetch())
    if result is None:
        console.print(f"[red]Experiment {exp_id!r} not found.[/red]")
        raise typer.Exit(code=1)

    generators = {"json": generate_json, "csv": generate_csv, "html": generate_html}
    content = generators[format](result)

    if output:
        output.write_text(content, encoding="utf-8")
        console.print(f"[green]Report written to {output}[/green]")
    else:
        print(content)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    app()


if __name__ == "__main__":
    main()
