from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from app.collectors.base import BaseCollector
from app.collectors.crawl4ai import Crawl4AICollector
from app.collectors.daily_hot import WeiboHotCollector
from app.collectors.rsshub import RSSHubCollector
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.hotspot_service import save_standard_hotspot


@dataclass(frozen=True)
class CollectorRunResult:
    """单个采集器的执行结果。"""

    collector_name: str
    collected_count: int = 0
    saved_count: int = 0
    error_message: str | None = None

    @property
    def succeeded(self) -> bool:
        """判断当前采集器是否执行成功。"""
        return self.error_message is None


@dataclass(frozen=True)
class CollectorsRunSummary:
    """一次手动采集任务的汇总结果。"""

    batch_id: str
    started_at: datetime
    finished_at: datetime
    results: list[CollectorRunResult] = field(default_factory=list)

    @property
    def total_collected_count(self) -> int:
        """返回本次采集到的热点总数。"""
        return sum(result.collected_count for result in self.results)

    @property
    def total_saved_count(self) -> int:
        """返回本次成功落盘的热点总数。"""
        return sum(result.saved_count for result in self.results)

    @property
    def failed_count(self) -> int:
        """返回本次执行失败的采集器数量。"""
        return sum(1 for result in self.results if not result.succeeded)


def build_manual_batch_id() -> str:
    """生成一次手动采集任务的批次号。"""
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return f"manual-{timestamp}-{uuid4().hex[:8]}"


def get_default_collectors() -> list[BaseCollector]:
    """返回当前默认启用的采集器列表。"""
    return [
        WeiboHotCollector(),
        RSSHubCollector(),
        Crawl4AICollector(),
    ]


def run_collectors_once(
    collectors: list[BaseCollector] | None = None,
    batch_id: str | None = None,
) -> CollectorsRunSummary:
    """执行一次所有已注册采集器并返回汇总结果。"""
    init_db()

    started_at = datetime.now(UTC)
    current_batch_id = batch_id or build_manual_batch_id()
    active_collectors = get_default_collectors() if collectors is None else collectors
    results: list[CollectorRunResult] = []

    with SessionLocal() as session:
        for collector in active_collectors:
            try:
                items = collector.collect()
                saved_count = 0
                for item in items:
                    save_standard_hotspot(
                        session=session,
                        item=item,
                        batch_id=current_batch_id,
                    )
                    saved_count += 1

                results.append(
                    CollectorRunResult(
                        collector_name=collector.name,
                        collected_count=len(items),
                        saved_count=saved_count,
                    )
                )
            except Exception as exc:
                results.append(
                    CollectorRunResult(
                        collector_name=collector.name,
                        error_message=str(exc),
                    )
                )

    return CollectorsRunSummary(
        batch_id=current_batch_id,
        started_at=started_at,
        finished_at=datetime.now(UTC),
        results=results,
    )
