from datetime import datetime

from pydantic import BaseModel, Field

from app.scheduler.runner import CollectorRunResult, CollectorsRunSummary


class CollectorRunResultResponse(BaseModel):
    """单个采集器执行结果响应。"""

    collector_name: str
    status: str
    collected_count: int
    saved_count: int
    error_message: str | None = None

    @classmethod
    def from_result(cls, result: CollectorRunResult) -> "CollectorRunResultResponse":
        """从采集器执行结果构建响应对象。"""
        return cls(
            collector_name=result.collector_name,
            status=result.status,
            collected_count=result.collected_count,
            saved_count=result.saved_count,
            error_message=result.error_message,
        )


class CollectRunResponse(BaseModel):
    """手动采集接口响应。"""

    batch_id: str
    started_at: datetime
    finished_at: datetime
    total_collected_count: int
    total_saved_count: int
    failed_count: int
    results: list[CollectorRunResultResponse] = Field(default_factory=list)

    @classmethod
    def from_summary(cls, summary: CollectorsRunSummary) -> "CollectRunResponse":
        """从采集汇总结果构建响应对象。"""
        return cls(
            batch_id=summary.batch_id,
            started_at=summary.started_at,
            finished_at=summary.finished_at,
            total_collected_count=summary.total_collected_count,
            total_saved_count=summary.total_saved_count,
            failed_count=summary.failed_count,
            results=[CollectorRunResultResponse.from_result(result) for result in summary.results],
        )
