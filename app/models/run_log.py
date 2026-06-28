from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CollectorRun(Base):
    """采集任务运行记录表。"""

    __tablename__ = "collector_runs"

    # 记录采集执行情况，便于后续排查失败和统计执行结果。
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    collector_name: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(20), index=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    item_count: Mapped[int] = mapped_column(Integer, default=0)
