"""
CLI entry point for modelrelay.
"""

import asyncio
import json
import sys
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from modelrelay import __version__
from modelrelay.sources import SOURCES, MODELS, get_available_models, get_best_model
from modelrelay.scores import SCORES
from modelrelay.router import ModelRouter, RouterConfig


console = Console()


@click.group()
@click.version_option(version=__version__)
def main():
    """ModelRelay - Intelligent LLM Model Routing"""
    pass


@main.command()
@click.option("--provider", "-p", help="Filter by provider")
@click.option("--min-score", "-m", type=float, help="Filter by minimum score")
@click.option("--sort-by", type=click.Choice(["score", "name", "provider"]), default="score", help="Sort results")
def models(provider: Optional[str], min_score: Optional[float], sort_by: str):
    """List available models."""
    models_list = get_available_models(provider=provider, min_score=min_score)

    if not models_list:
        console.print("[yellow]No models found matching criteria[/yellow]")
        return

    # Sort
    if sort_by == "score":
        models_list.sort(key=lambda m: m.score or 0, reverse=True)
    elif sort_by == "name":
        models_list.sort(key=lambda m: m.display_name.lower())
    elif sort_by == "provider":
        models_list.sort(key=lambda m: (m.provider, m.display_name))

    table = Table(title=f"Available Models ({len(models_list)} total)")
    table.add_column("Model ID", style="cyan")
    table.add_column("Display Name", style="green")
    table.add_column("Score", justify="right")
    table.add_column("Context", style="dim")
    table.add_column("Provider", style="magenta")

    for m in models_list:
        score_str = f"{m.score:.3f}" if m.score else "-"
        table.add_row(m.model_id, m.display_name, score_str, m.context, m.provider)

    console.print(table)


@main.command()
@click.option("--provider", "-p", help="Preferred provider")
def best(provider: Optional[str]):
    """Show the best available model."""
    model = get_best_model(provider=provider)

    if not model:
        console.print("[red]No models available[/red]")
        return

    panel = Panel(
        f"[cyan]Model ID:[/cyan] {model.model_id}\n"
        f"[green]Display Name:[/green] {model.display_name}\n"
        f"[yellow]Score:[/yellow] {model.score:.3f}\n"
        f"[dim]Context:[/dim] {model.context}\n"
        f"[magenta]Provider:[/magenta] {model.provider}",
        title="Best Available Model",
        border_style="green",
    )
    console.print(panel)


@main.command()
def providers():
    """List all providers."""
    table = Table(title="Configured Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("URL", style="dim")
    table.add_column("Models", justify="right")

    for key, provider in SOURCES.items():
        model_count = len(provider.get("models", []))
        table.add_row(key, provider["name"], provider["url"], str(model_count))

    console.print(table)


@main.command()
def scores():
    """Show model quality scores."""
    # Sort by score descending
    sorted_scores = sorted(SCORES.items(), key=lambda x: x[1], reverse=True)

    table = Table(title=f"Model Scores ({len(sorted_scores)} total)")
    table.add_column("Model ID", style="cyan")
    table.add_column("Score", justify="right", style="yellow")

    for model_id, score in sorted_scores[:50]:  # Show top 50
        table.add_row(model_id, f"{score:.3f}")

    if len(sorted_scores) > 50:
        console.print(f"[dim]... and {len(sorted_scores) - 50} more[/dim]")

    console.print(table)


@main.command()
@click.option("--host", default="0.0.0.0", help="Server host")
@click.option("--port", default=8000, help="Server port")
@click.option("--timeout", default=30.0, help="Request timeout in seconds")
def serve(host: str, port: int, timeout: float):
    """Start the modelrelay HTTP server."""
    console.print(f"[green]Starting ModelRelay server on {host}:{port}[/green]")

    try:
        import uvicorn
    except ImportError:
        console.print("[red]Error: uvicorn not installed. Install with: pip install uvicorn[/red]")
        sys.exit(1)

    from modelrelay.server import create_app

    config = RouterConfig(timeout_seconds=timeout)
    app = create_app(config)

    uvicorn.run(app, host=host, port=port)


@main.command()
@click.option("--provider", "-p", help="Provider to check")
def check(provider: Optional[str]):
    """Check provider availability."""
    async def do_check():
        config = RouterConfig(check_timeout_seconds=5.0)
        router = ModelRouter(config)

        providers_to_check = [provider] if provider else list(SOURCES.keys())

        table = Table(title="Provider Status")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Latency", justify="right")
        table.add_column("Error", style="red")

        for p in providers_to_check:
            status = await router.check_provider(p)

            status_str = "[green]✓ Available[/green]" if status.available else "[red]✗ Unavailable[/red]"
            latency_str = f"{status.latency_ms:.0f}ms" if status.latency_ms else "-"
            error_str = status.error or ""

            table.add_row(p, status_str, latency_str, error_str)

        console.print(table)
        await router.close()

    asyncio.run(do_check())


@main.command()
@click.argument("model_id")
def info(model_id: str):
    """Show detailed info about a model."""
    # Find model
    target = None
    for m in MODELS:
        if m.model_id == model_id:
            target = m
            break

    if not target:
        console.print(f"[red]Model not found: {model_id}[/red]")
        console.print("\n[yellow]Tip: Use 'modelrelay models' to list available models[/yellow]")
        return

    provider = SOURCES.get(target.provider, {})

    panel = Panel(
        f"[cyan]Model ID:[/cyan] {target.model_id}\n"
        f"[green]Display Name:[/green] {target.display_name}\n"
        f"[yellow]Score:[/yellow] {target.score:.3f}\n"
        f"[dim]Context Window:[/dim] {target.context}\n"
        f"[magenta]Provider:[/magenta] {target.provider} ({provider.get('name', 'Unknown')})\n"
        f"[blue]API URL:[/blue] {target.url}",
        title=f"Model Info: {target.display_name}",
        border_style="cyan",
    )
    console.print(panel)


if __name__ == "__main__":
    main()
