from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.hotspot import StandardHotspot


class HotspotItem(BaseModel):
    """阶段一统一使用的标准热点对象。"""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        ...,
        description="标准化后的热点标题，阶段一必填。",
        min_length=1,
    )
    summary: str | None = Field(
        default=None,
        description="摘要或正文提炼，阶段一允许为空。",
    )
    source_platform: str = Field(
        ...,
        description="来源平台，例如 weibo、zhihu、reddit。",
        min_length=1,
    )
    source_channel: str = Field(
        ...,
        description="来源榜单或频道名称，例如 hot_search、top_news。",
        min_length=1,
    )
    source_url: str | None = Field(
        default=None,
        description="原始详情页或榜单链接。",
    )
    rank: int | None = Field(
        default=None,
        description="来源榜单中的排名，阶段一允许为空。",
        ge=1,
    )
    score: str | None = Field(
        default=None,
        description="原始热度值，统一按字符串保存。",
    )
    published_at: datetime | None = Field(
        default=None,
        description="来源提供的原始发布时间，阶段一允许为空。",
    )
    fetched_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="系统采集时间。",
    )
    region: str = Field(
        default="cn",
        description="区域标记，例如 cn 或 global。",
        min_length=1,
    )
    language: str = Field(
        default="zh-CN",
        description="语言标记，例如 zh-CN 或 en。",
        min_length=1,
    )
    raw_payload: dict = Field(
        default_factory=dict,
        description="原始返回内容，便于追溯和后续重处理。",
    )

    @field_validator("title", "source_platform", "source_channel", "region", "language")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        """清理必填字符串并阻止空值进入标准对象。"""
        value = value.strip()
        if not value:
            raise ValueError("field cannot be blank")
        return value

    @field_validator("summary")
    @classmethod
    def normalize_summary(cls, value: str | None) -> str | None:
        """将空白摘要归一化为 None。"""
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("source_url")
    @classmethod
    def normalize_source_url(cls, value: str | None) -> str | None:
        """清理来源链接中的空白字符。"""
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("score")
    @classmethod
    def normalize_score(cls, value: str | None) -> str | None:
        """清理原始热度值中的空白字符。"""
        if value is None:
            return None
        value = value.strip()
        return value or None

    @classmethod
    def required_stage_one_fields(cls) -> tuple[str, ...]:
        """返回阶段一标准对象的必填字段列表。"""
        return ("title", "source_platform", "source_channel")


class StandardHotspotResponse(BaseModel):
    """标准热点接口响应结构。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: str
    title: str
    summary: str | None = None
    source_platform: str
    source_channel: str
    source_url: str | None = None
    rank: int | None = None
    score: str | None = None
    published_at: datetime | None = None
    fetched_at: datetime
    region: str
    language: str
    raw_payload: dict[str, Any] | None = None

    @classmethod
    def from_model(cls, hotspot: StandardHotspot) -> "StandardHotspotResponse":
        """从标准热点 ORM 对象构建响应对象。"""
        return cls.model_validate(hotspot)
