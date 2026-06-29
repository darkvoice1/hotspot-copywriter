from app.collectors.crawl4ai import Crawl4AICollector
from app.collectors.daily_hot import WeiboHotCollector
from app.collectors.rsshub import RSSHubCollector
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.hotspot_service import save_standard_hotspot


def run_collectors_once() -> None:
    """执行一次所有已注册采集器。"""
    # 先确保本地数据库表存在，便于后续任务直接落盘。
    init_db()

    collectors = [
        WeiboHotCollector(),
        RSSHubCollector(),
        Crawl4AICollector(),
    ]

    with SessionLocal() as session:
        for collector in collectors:
            for item in collector.collect():
                save_standard_hotspot(
                    session=session,
                    item=item,
                    batch_id="manual-run",
                )
