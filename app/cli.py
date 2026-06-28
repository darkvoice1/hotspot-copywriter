import typer

from app.scheduler.runner import run_collectors_once

app = typer.Typer(help="Hotspot collection project CLI")


@app.command()
def collect() -> None:
    """手动执行一次热点采集流程。"""
    # 当前先复用统一执行入口，后续再扩展按来源执行等能力。
    run_collectors_once()
    typer.echo("Collectors executed.")
