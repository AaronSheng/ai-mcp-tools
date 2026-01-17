"""API Adapter - RESTful API 入口

提供 HTTP RESTful API 接口。
"""

from fastapi import APIRouter
from app.api.request.supplier_order_response import router as stock_outage_router

# 创建主路由（不设置前缀，由挂载时决定）
api_router = APIRouter(tags=["HTTP API"])

# 注册子路由
api_router.include_router(stock_outage_router)

__all__ = ["api_router"]