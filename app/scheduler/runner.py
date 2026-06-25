from app.collectors.crawl4ai import Crawl4AICollector
from app.collectors.daily_hot import DailyHotCollector
from app.collectors.rsshub import RSSHubCollector
from app.db.base import Base
from app.db.session import engine


def run_collectors_once() -> None:
    Base.metadata.create_all(bind=engine)

    collectors = [
        DailyHotCollector(),
        RSSHubCollector(),
        Crawl4AICollector(),
    ]

    for collector in collectors:
        collector.collect()
