from collections.abc import Callable

from apscheduler.schedulers.blocking import BlockingScheduler

from app.scheduler.runner import CollectorsRunSummary, run_scheduled_collectors_once


DEFAULT_DAILY_COLLECT_HOUR = 8
DEFAULT_DAILY_COLLECT_MINUTE = 0


def create_daily_collect_scheduler(
    job_func: Callable[[], CollectorsRunSummary] = run_scheduled_collectors_once,
    hour: int = DEFAULT_DAILY_COLLECT_HOUR,
    minute: int = DEFAULT_DAILY_COLLECT_MINUTE,
) -> BlockingScheduler:
    """创建每日热点采集调度器。"""
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(
        job_func,
        trigger="cron",
        hour=hour,
        minute=minute,
        id="daily_hotspot_collect",
        replace_existing=True,
    )
    return scheduler


def start_daily_collect_scheduler(
    hour: int = DEFAULT_DAILY_COLLECT_HOUR,
    minute: int = DEFAULT_DAILY_COLLECT_MINUTE,
) -> None:
    """启动每日热点采集调度器。"""
    scheduler = create_daily_collect_scheduler(hour=hour, minute=minute)
    scheduler.start()
