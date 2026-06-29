from app.collectors.daily_hot import WeiboHotCollector
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.hotspot import StandardHotspot
from app.services.hotspot_service import save_standard_hotspot


def test_map_weibo_response_to_hotspot_items() -> None:
    """验证微博热搜响应可以映射为标准热点对象。"""
    collector = WeiboHotCollector()
    payload = {
        "data": {
            "realtime": [
                {
                    "mid": "weibo-1",
                    "word": "测试微博热点",
                    "word_scheme": "#测试微博热点#",
                    "num": 12345,
                    "onboard_time": 1766995200,
                }
            ]
        }
    }

    items = collector.map_response(payload)

    assert len(items) == 1
    assert items[0].title == "测试微博热点"
    assert items[0].source_platform == "weibo"
    assert items[0].source_channel == "热搜榜"
    assert items[0].rank == 1
    assert items[0].score == "12345"


def test_save_weibo_hot_item_to_database() -> None:
    """验证微博热搜映射结果可以成功落盘。"""
    init_db()
    collector = WeiboHotCollector()
    items = collector.map_response(
        {
            "data": {
                "realtime": [
                    {
                        "word": "可落盘热点",
                        "word_scheme": "#可落盘热点#",
                    }
                ]
            }
        }
    )

    with SessionLocal() as session:
        saved_hotspot = save_standard_hotspot(
            session=session,
            item=items[0],
            batch_id="weibo-test-batch",
        )
        loaded_hotspot = session.get(StandardHotspot, saved_hotspot.id)

    assert loaded_hotspot is not None
    assert loaded_hotspot.title == "可落盘热点"
    assert loaded_hotspot.source_platform == "weibo"
