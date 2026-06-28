import typer

from app.db.init_db import init_db
from app.scheduler.runner import run_collectors_once

app = typer.Typer(help="Hotspot collection project CLI")


@app.command()
def collect() -> None:
    """手动执行一次热点采集流程。"""
    # 当前先复用统一执行入口，后续再扩展按来源执行等能力。
    run_collectors_once()
    typer.echo("Collectors executed.")


@app.command("init-db")
def init_database() -> None:
    """初始化本地 SQLite 表结构。"""
    table_names = init_db()
    typer.echo("Database initialized successfully.")
    typer.echo(f"Tables: {', '.join(table_names)}")
