from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """提供基础健康检查接口。"""
    return {"status": "ok"}
