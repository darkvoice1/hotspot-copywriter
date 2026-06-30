from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from app.collectors.base import BaseCollector
from app.collectors.crawl4ai import Crawl4AICollector
from app.collectors.daily_hot import WeiboHotCollector
from app.collectors.rsshub import RSSHubCollector
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.run_log import CollectorRun
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

    @property
    def status(self) -> str:
        """返回适合落库保存的执行状态。"""
        return "success" if self.succeeded else "failed"


@dataclass(frozen=True)
class CollectorsRunSummary:
    """一次采集任务的汇总结果。"""

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


def build_batch_id(prefix: str = "manual") -> str:
    """生成一次采集任务的批次号。"""
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{timestamp}-{uuid4().hex[:8]}"


def build_manual_batch_id() -> str:
    """生成一次手动采集任务的批次号。"""
    return build_batch_id("manual")


def build_scheduled_batch_id() -> str:
    """生成一次定时采集任务的批次号。"""
    return build_batch_id("scheduled")


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

                result = CollectorRunResult(
                    collector_name=collector.name,
                    collected_count=len(items),
                    saved_count=saved_count,
                )
            except Exception as exc:
                result = CollectorRunResult(
                    collector_name=collector.name,
                    error_message=str(exc),
                )

            results.append(result)
            _save_collector_run(
                session=session,
                batch_id=current_batch_id,
                result=result,
                started_at=started_at,
                finished_at=datetime.now(UTC),
            )

    return CollectorsRunSummary(
        batch_id=current_batch_id,
        started_at=started_at,
        finished_at=datetime.now(UTC),
        results=results,
    )


def run_scheduled_collectors_once() -> CollectorsRunSummary:
    """执行一次定时采集任务。"""
    return run_collectors_once(batch_id=build_scheduled_batch_id())


def _save_collector_run(
    session,
    batch_id: str,
    result: CollectorRunResult,
    started_at: datetime,
    finished_at: datetime,
) -> CollectorRun:
    """保存单个采集器的运行记录。"""
    run_log = CollectorRun(
        batch_id=batch_id,
        collector_name=result.collector_name,
        status=result.status,
        message=result.error_message,
        started_at=started_at,
        finished_at=finished_at,
        item_count=result.saved_count,
    )
    session.add(run_log)
    session.commit()
    session.refresh(run_log)
    return run_log
