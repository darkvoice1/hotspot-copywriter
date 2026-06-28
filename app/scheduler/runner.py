from app.collectors.crawl4ai import Crawl4AICollector
from app.collectors.daily_hot import DailyHotCollector
from app.collectors.rsshub import RSSHubCollector
from app.db.base import Base
from app.db.session import engine


def run_collectors_once() -> None:
    """执行一次所有已注册采集器。"""
    # 先确保本地数据库表存在，便于后续任务直接落盘。
    Base.metadata.create_all(bind=engine)

    collectors = [
        DailyHotCollector(),
        RSSHubCollector(),
        Crawl4AICollector(),
    ]

    # 依次执行采集器，当前阶段先验证主链路结构可用。
    for collector in collectors:
        collector.collect()
