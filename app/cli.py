import typer

from app.db.init_db import init_db
from app.scheduler.runner import CollectorsRunSummary, run_collectors_once

app = typer.Typer(help="Hotspot collection project CLI")


def _print_collect_summary(summary: CollectorsRunSummary) -> None:
    """打印一次手动采集任务的执行摘要。"""
    typer.echo(f"批次号: {summary.batch_id}")
    typer.echo(f"采集器数量: {len(summary.results)}")
    typer.echo(f"采集热点数: {summary.total_collected_count}")
    typer.echo(f"成功落盘数: {summary.total_saved_count}")
    typer.echo(f"失败采集器数: {summary.failed_count}")

    for result in summary.results:
        status = "成功" if result.succeeded else "失败"
        typer.echo(
            f"- {result.collector_name}: {status}, "
            f"采集 {result.collected_count} 条, 落盘 {result.saved_count} 条"
        )
        if result.error_message:
            typer.echo(f"  错误: {result.error_message}")


@app.command()
def collect() -> None:
    """手动执行一次热点采集流程。"""
    summary = run_collectors_once()
    _print_collect_summary(summary)


@app.command("init-db")
def init_database() -> None:
    """初始化本地 SQLite 表结构。"""
    table_names = init_db()
    typer.echo("Database initialized successfully.")
    typer.echo(f"Tables: {', '.join(table_names)}")


def main() -> None:
    """启动命令行应用。"""
    app()


if __name__ == "__main__":
    main()
