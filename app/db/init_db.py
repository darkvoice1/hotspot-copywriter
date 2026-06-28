from sqlalchemy import inspect

from app.db.base import Base
from app.db.session import engine
from app.models.hotspot import RawHotspot, StandardHotspot
from app.models.run_log import CollectorRun


def init_db() -> list[str]:
    """初始化数据库表结构并返回当前表名列表。"""
    # 提前引用模型，确保 SQLAlchemy 元数据中已经注册所有表。
    _ = (RawHotspot, StandardHotspot, CollectorRun)

    Base.metadata.create_all(bind=engine)
    return get_table_names()


def get_table_names() -> list[str]:
    """返回当前数据库中的表名列表。"""
    inspector = inspect(engine)
    return sorted(inspector.get_table_names())
