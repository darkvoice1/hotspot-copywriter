from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

import app.api.collect_runs as collect_runs
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.main import create_app
from app.scheduler.runner import CollectorRunResult, CollectorsRunSummary
from app.schemas.hotspot import HotspotItem
from app.schemas.organized_hotspot import OrganizedHotspotItem
from app.services.hotspot_service import save_standard_hotspot
from app.services.organize_service import save_organized_hotspot


def test_health_api_returns_ok() -> None:
    """验证健康检查接口返回正常状态。"""
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_collect_run_api_returns_summary(monkeypatch) -> None:
    """验证手动采集接口会返回采集汇总。"""

    def fake_run_collectors_once() -> CollectorsRunSummary:
        """构造测试用采集汇总。"""
        now = datetime.now(UTC)
        return CollectorsRunSummary(
            batch_id="manual-api-test",
            started_at=now,
            finished_at=now,
            results=[
                CollectorRunResult(
                    collector_name="fake_collector",
                    collected_count=2,
                    saved_count=2,
                )
            ],
        )

    monkeypatch.setattr(collect_runs, "run_collectors_once", fake_run_collectors_once)
    client = TestClient(create_app())

    response = client.post("/collect-runs")

    assert response.status_code == 200
    data = response.json()
    assert data["batch_id"] == "manual-api-test"
    assert data["total_collected_count"] == 2
    assert data["total_saved_count"] == 2
    assert data["failed_count"] == 0
    assert data["results"][0]["collector_name"] == "fake_collector"
    assert data["results"][0]["status"] == "success"


def test_list_standard_hotspots_api_returns_batch_items() -> None:
    """验证阶段一标准热点批次查询接口。"""
    init_db()
    batch_id = f"api-standard-batch-{uuid4().hex}"

    with SessionLocal() as session:
        save_standard_hotspot(
            session=session,
            item=HotspotItem(
                title="接口测试热点",
                source_platform="weibo",
                source_channel="热搜榜",
                rank=1,
                raw_payload={"from": "api-test"},
            ),
            batch_id=batch_id,
        )

    client = TestClient(create_app())
    response = client.get("/hotspots/standard", params={"batch_id": batch_id})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["batch_id"] == batch_id
    assert data[0]["title"] == "接口测试热点"
    assert data[0]["source_platform"] == "weibo"


def test_list_organized_hotspots_api_returns_batch_items() -> None:
    """验证阶段二整理结果批次查询接口。"""
    init_db()
    batch_id = f"api-organized-batch-{uuid4().hex}"

    with SessionLocal() as session:
        save_organized_hotspot(
            session=session,
            item=OrganizedHotspotItem(
                batch_id=batch_id,
                topic_title="接口测试主题",
                representative_hotspot_id=1,
                source_hotspot_ids=[1, 2],
                source_platforms=["weibo", "douyin"],
                category="娱乐",
                tags=["明星"],
                summary="接口测试主题摘要。",
            ),
        )

    client = TestClient(create_app())
    response = client.get("/hotspots/organized", params={"batch_id": batch_id})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["batch_id"] == batch_id
    assert data[0]["topic_title"] == "接口测试主题"
    assert data[0]["source_platforms"] == ["weibo", "douyin"]
    assert data[0]["tags"] == ["明星"]

