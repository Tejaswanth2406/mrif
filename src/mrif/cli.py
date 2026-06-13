"""
MRIF Command-Line Interface.

Usage:
    mrif init
    mrif status
    mrif spawn --goal "cancer_research"
    mrif observe --json '{"knowledge": {"concepts": [{"id": "protein-folding"}]}}'
    mrif research "What causes Alzheimer's?"
    mrif audit --last 10
    mrif evolution
"""
from __future__ import annotations

import json
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from mrif.config import settings
from mrif.core.meta_core import MetaCore
from mrif.research.pipeline import ResearchPipeline
from mrif.utils.logging import configure_logging

app = typer.Typer(name="mrif", help="Meta-Recursive Intelligence Framework CLI")
console = Console()

# Global MetaCore instance (per CLI session)
_core: MetaCore | None = None


def _get_core() -> MetaCore:
    global _core
    if _core is None:
        _core = MetaCore()
    return _core


@app.callback()
def main() -> None:
    configure_logging()


@app.command()
def init(
    core_id: str = typer.Option(settings.core_id, help="Core identifier"),
) -> None:
    """Initialise a new MetaCore instance."""
    global _core
    _core = MetaCore(core_id=core_id)
    rprint(f"[green]✓[/green] MetaCore '{core_id}' initialised.")


@app.command()
def status() -> None:
    """Display the current MetaCore state summary."""
    summary = _get_core().get_summary()
    table = Table(title="MetaCore Status", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    for k, v in summary.items():
        table.add_row(str(k), str(v))
    console.print(table)


@app.command()
def spawn(
    goal: str = typer.Option(..., help="Goal for the new agent"),
    permissions: Optional[str] = typer.Option(
        None, help="Comma-separated permission list"
    ),
) -> None:
    """Spawn a descendant agent."""
    perms = permissions.split(",") if permissions else None
    clone_id = _get_core().spawn_clone(goal=goal, permissions=perms)
    rprint(f"[green]✓[/green] Spawned clone: [bold]{clone_id}[/bold]")


@app.command()
def observe(
    payload: str = typer.Argument(..., help="JSON observation string"),
) -> None:
    """Inject an observation into the MetaCore."""
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        rprint(f"[red]✗[/red] Invalid JSON: {exc}")
        raise typer.Exit(1)
    _get_core().observe(data)
    rprint("[green]✓[/green] Observation ingested.")


@app.command()
def research(
    question: str = typer.Argument(..., help="Research question"),
    domain: str = typer.Option("general", help="Scientific domain"),
) -> None:
    """Run the autonomous research pipeline."""
    pipeline = ResearchPipeline(max_hypotheses=3)
    rprint(f"[bold]Running pipeline for:[/bold] {question}")
    run = pipeline.run(question, domain=domain)
    rprint(f"\n[bold]State:[/bold] {run.state}")
    if run.findings:
        for k, v in run.findings.items():
            rprint(f"  [cyan]{k}[/cyan]: {v}")
    if run.error:
        rprint(f"[red]Error:[/red] {run.error}")


@app.command()
def audit(
    last: int = typer.Option(10, help="Number of recent entries to show"),
) -> None:
    """Display the audit log."""
    entries = _get_core().audit.get_recent(last)
    table = Table(title=f"Audit Log (last {last})")
    table.add_column("ID", style="dim")
    table.add_column("Type", style="cyan")
    table.add_column("Model", style="yellow")
    table.add_column("Timestamp")
    for e in entries:
        table.add_row(
            str(e["id"]),
            e["event_type"],
            e["model_id"],
            str(e["timestamp"]),
        )
    console.print(table)


@app.command()
def evolution() -> None:
    """Show the evolution fitness trend."""
    core = _get_core()
    trend = core.evolution.fitness_trend(10)
    rprint(f"[bold]Current fitness:[/bold] {core.evolution.current_fitness():.4f}")
    rprint(f"[bold]Peak fitness:[/bold]    {core.evolution.peak_fitness():.4f}")
    rprint(f"[bold]Improving:[/bold]       {core.evolution.is_improving()}")
    rprint(f"[bold]Trend (last 10):[/bold] {[round(f, 3) for f in trend]}")


if __name__ == "__main__":
    app()
