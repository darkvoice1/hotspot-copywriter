import typer

from app.scheduler.runner import run_collectors_once

app = typer.Typer(help="Hotspot collection project CLI")


@app.command()
def collect() -> None:
    """Run the hotspot collectors once."""
    run_collectors_once()
    typer.echo("Collectors executed.")
