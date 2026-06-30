from app.scheduler.jobs import create_daily_collect_scheduler
from app.scheduler.runner import CollectorsRunSummary


def test_create_daily_collect_scheduler_registers_daily_job() -> None:
    """验证每日采集调度器会注册 cron 任务。"""

    def fake_job() -> CollectorsRunSummary:
        """测试用空任务。"""
        raise AssertionError("调度器注册测试不应真正执行任务")

    scheduler = create_daily_collect_scheduler(job_func=fake_job, hour=7, minute=30)
    jobs = scheduler.get_jobs()

    assert len(jobs) == 1
    assert jobs[0].id == "daily_hotspot_collect"
    assert str(jobs[0].trigger) == "cron[hour='7', minute='30']"
