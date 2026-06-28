from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例。"""
    # 注册基础应用和路由，后续阶段再逐步补齐接口。
    app = FastAPI(title=settings.app_name)
    app.include_router(router)
    return app


app = create_app()
