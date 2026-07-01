from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.schemas.organized_hotspot import OrganizedHotspotItem
from app.services.organize_service import (
    get_organized_hotspot,
    list_organized_hotspots_by_batch,
    save_organized_hotspot,
)


def test_save_and_read_organized_hotspot() -> None:
    """验证阶段二整理结果可以写入并读回。"""
    init_db()
    batch_id = f"organized-test-batch-{uuid4().hex}"
    item = OrganizedHotspotItem(
        batch_id=batch_id,
        topic_title="测试热点主题",
        representative_hotspot_id=1,
        source_hotspot_ids=[1, 2],
        source_platforms=["weibo", "douyin"],
        category="娱乐",
        tags=["明星", "官宣"],
        summary="测试热点主题正在多平台发酵。",
    )

    with SessionLocal() as session:
        saved_hotspot = save_organized_hotspot(session=session, item=item)
        loaded_hotspot = get_organized_hotspot(session, saved_hotspot.id)

    assert loaded_hotspot is not None
    assert loaded_hotspot.batch_id == batch_id
    assert loaded_hotspot.topic_title == "测试热点主题"
    assert loaded_hotspot.representative_hotspot_id == 1
    assert loaded_hotspot.source_hotspot_ids == [1, 2]
    assert loaded_hotspot.source_platforms == ["weibo", "douyin"]
    assert loaded_hotspot.category == "娱乐"
    assert loaded_hotspot.tags == ["明星", "官宣"]
    assert loaded_hotspot.summary == "测试热点主题正在多平台发酵。"
    assert loaded_hotspot.organize_version == "v1"


def test_list_organized_hotspots_by_batch() -> None:
    """验证可以按批次读取阶段二整理结果。"""
    init_db()
    batch_id = f"organized-list-batch-{uuid4().hex}"

    with SessionLocal() as session:
        save_organized_hotspot(
            session=session,
            item=OrganizedHotspotItem(
                batch_id=batch_id,
                topic_title="热点甲",
                representative_hotspot_id=1,
                source_hotspot_ids=[1],
                source_platforms=["weibo"],
            ),
        )
        save_organized_hotspot(
            session=session,
            item=OrganizedHotspotItem(
                batch_id=batch_id,
                topic_title="热点乙",
                representative_hotspot_id=2,
                source_hotspot_ids=[2],
                source_platforms=["bilibili"],
            ),
        )

        loaded_hotspots = list_organized_hotspots_by_batch(session=session, batch_id=batch_id)

    assert [hotspot.topic_title for hotspot in loaded_hotspots] == ["热点甲", "热点乙"]


def test_organized_hotspot_item_normalizes_string_lists() -> None:
    """验证整理结果对象会清理标签和来源平台中的重复空白项。"""
    item = OrganizedHotspotItem(
        batch_id="batch-001",
        topic_title="  测试热点  ",
        representative_hotspot_id=1,
        source_hotspot_ids=[1],
        source_platforms=[" weibo ", "", "weibo", "douyin"],
        tags=[" 科技 ", "", "科技", "AI"],
        summary="   ",
    )

    assert item.topic_title == "测试热点"
    assert item.source_platforms == ["weibo", "douyin"]
    assert item.tags == ["科技", "AI"]
    assert item.summary is None


def test_organized_hotspot_item_rejects_invalid_source_ids() -> None:
    """验证整理结果对象会拒绝非法来源热点 ID。"""
    with pytest.raises(ValidationError):
        OrganizedHotspotItem(
            batch_id="batch-001",
            topic_title="测试热点",
            representative_hotspot_id=1,
            source_hotspot_ids=[0],
            source_platforms=["weibo"],
        )
