from uuid import uuid4

from sqlalchemy import select

from app.collectors.base import BaseCollector
from app.db.session import SessionLocal
from app.models.hotspot import StandardHotspot
from app.models.run_log import CollectorRun
from app.scheduler.runner import run_collectors_once, run_scheduled_collectors_once
from app.schemas.hotspot import HotspotItem


class FakeSuccessCollector(BaseCollector):
    """测试用成功采集器。"""

    name = "fake_success"

    def collect(self) -> list[HotspotItem]:
        """返回一条稳定的测试热点。"""
        return [
            HotspotItem(
                title="手动入口测试热点",
                source_platform="unit_test",
                source_channel="manual_collect",
                raw_payload={"from": "fake_success"},
            )
        ]


class FakeFailedCollector(BaseCollector):
    """测试用失败采集器。"""

    name = "fake_failed"

    def collect(self) -> list[HotspotItem]:
        """模拟采集器执行失败。"""
        raise RuntimeError("模拟采集失败")


def test_run_collectors_once_returns_summary_and_saves_items() -> None:
    """验证手动执行入口可以采集、落盘并返回摘要。"""
    batch_id = f"manual-test-batch-{uuid4().hex}"

    summary = run_collectors_once(
        collectors=[FakeSuccessCollector()],
        batch_id=batch_id,
    )

    with SessionLocal() as session:
        records = session.scalars(
            select(StandardHotspot).where(StandardHotspot.batch_id == batch_id)
        ).all()

    assert summary.batch_id == batch_id
    assert summary.total_collected_count == 1
    assert summary.total_saved_count == 1
    assert summary.failed_count == 0
    assert len(records) == 1
    assert records[0].title == "手动入口测试热点"


def test_run_collectors_once_records_success_run_log() -> None:
    """验证成功采集器会保存运行记录。"""
    batch_id = f"manual-run-log-test-{uuid4().hex}"

    run_collectors_once(
        collectors=[FakeSuccessCollector()],
        batch_id=batch_id,
    )

    with SessionLocal() as session:
        run_logs = session.scalars(
            select(CollectorRun).where(CollectorRun.batch_id == batch_id)
        ).all()

    assert len(run_logs) == 1
    assert run_logs[0].collector_name == "fake_success"
    assert run_logs[0].status == "success"
    assert run_logs[0].item_count == 1
    assert run_logs[0].message is None
    assert run_logs[0].finished_at is not None


def test_run_collectors_once_records_failed_collector() -> None:
    """验证单个采集器失败时入口会记录错误并继续返回摘要。"""
    batch_id = f"manual-failed-test-batch-{uuid4().hex}"

    summary = run_collectors_once(
        collectors=[FakeFailedCollector()],
        batch_id=batch_id,
    )

    with SessionLocal() as session:
        run_logs = session.scalars(
            select(CollectorRun).where(CollectorRun.batch_id == batch_id)
        ).all()

    assert summary.total_collected_count == 0
    assert summary.total_saved_count == 0
    assert summary.failed_count == 1
    assert summary.results[0].collector_name == "fake_failed"
    assert summary.results[0].error_message == "模拟采集失败"
    assert len(run_logs) == 1
    assert run_logs[0].status == "failed"
    assert run_logs[0].message == "模拟采集失败"


def test_run_scheduled_collectors_once_uses_scheduled_batch_prefix() -> None:
    """验证定时采集入口会使用定时任务批次前缀。"""
    summary = run_scheduled_collectors_once()

    assert summary.batch_id.startswith("scheduled-")
