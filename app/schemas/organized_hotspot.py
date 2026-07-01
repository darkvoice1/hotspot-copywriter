from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.organized_hotspot import OrganizedHotspot


class OrganizedHotspotItem(BaseModel):
    """阶段二整理结果的标准对象。"""

    model_config = ConfigDict(extra="forbid")

    batch_id: str = Field(..., description="阶段一采集批次号。", min_length=1)
    topic_title: str = Field(..., description="整理后的热点主题标题。", min_length=1)
    representative_hotspot_id: int = Field(..., description="代表热点记录 ID。", ge=1)
    source_hotspot_ids: list[int] = Field(
        ...,
        description="参与聚合的标准热点记录 ID 列表。",
        min_length=1,
    )
    source_platforms: list[str] = Field(
        ...,
        description="参与聚合的来源平台列表。",
        min_length=1,
    )
    category: str | None = Field(default=None, description="热点分类，后续规则分类任务填充。")
    tags: list[str] = Field(default_factory=list, description="热点标签列表。")
    summary: str | None = Field(default=None, description="热点事实摘要。")
    organize_version: str = Field(default="v1", description="整理逻辑版本。", min_length=1)

    @field_validator("batch_id", "topic_title", "organize_version")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        """清理必填字符串并阻止空值进入整理结果。"""
        value = value.strip()
        if not value:
            raise ValueError("field cannot be blank")
        return value

    @field_validator("category", "summary")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        """将可选字符串中的空白内容归一化为 None。"""
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("source_hotspot_ids")
    @classmethod
    def validate_source_hotspot_ids(cls, value: list[int]) -> list[int]:
        """校验来源热点 ID 列表。"""
        if any(item <= 0 for item in value):
            raise ValueError("source_hotspot_ids must be positive")
        return value

    @field_validator("source_platforms", "tags")
    @classmethod
    def normalize_string_list(cls, value: list[str]) -> list[str]:
        """清理字符串列表中的空白项并去重。"""
        normalized_items: list[str] = []
        for item in value:
            normalized_item = item.strip()
            if normalized_item and normalized_item not in normalized_items:
                normalized_items.append(normalized_item)
        return normalized_items


class OrganizedHotspotResponse(BaseModel):
    """阶段二整理结果接口响应结构。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: str
    topic_title: str
    representative_hotspot_id: int
    source_hotspot_ids: list[int]
    source_platforms: list[str]
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    summary: str | None = None
    organize_version: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, hotspot: OrganizedHotspot) -> "OrganizedHotspotResponse":
        """从整理结果 ORM 对象构建响应对象。"""
        return cls.model_validate(hotspot)
