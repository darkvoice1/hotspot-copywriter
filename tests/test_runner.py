from uuid import uuid4

from sqlalchemy import select

from app.collectors.base import BaseCollector
from app.db.session import SessionLocal
from app.models.hotspot import StandardHotspot
from app.scheduler.runner import run_collectors_once
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


def test_run_collectors_once_records_failed_collector() -> None:
    """验证单个采集器失败时入口会记录错误并继续返回摘要。"""
    summary = run_collectors_once(
        collectors=[FakeFailedCollector()],
        batch_id=f"manual-failed-test-batch-{uuid4().hex}",
    )

    assert summary.total_collected_count == 0
    assert summary.total_saved_count == 0
    assert summary.failed_count == 1
    assert summary.results[0].collector_name == "fake_failed"
    assert summary.results[0].error_message == "模拟采集失败"


