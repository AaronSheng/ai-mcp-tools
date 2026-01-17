"""断码订单 HTTP API

提供断码订单相关的 RESTful API 接口。
"""

import random
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.common.logging import get_logger
from app.common.config import settings
from app.api.response import (
    RandomOrderData,
    TransferOrderData,
    ContactMaterialDepartmentData,
    UpdateProductionScheduleData,
    RecordExceptionData,
)

logger = get_logger(__name__)

# 创建路由
router = APIRouter(prefix="/supplierOrder", tags=["Supplier Order"])

# 根据配置选择服务实现
if settings.app.use_mock_data:
    logger.info("Stock Outage API: Using MOCK data mode")
    # from app.service.stock_outage.stock_outage_mock_service import (
    #     query_orders_mock as query_orders_service,
    #     get_supplier_capacity_info_mock as get_supplier_capacity_info_service,
    # )
else:
    logger.info("Stock Outage API: Using DATABASE mode")
    # from app.service.stock_outage.stock_outage_service import (
    #     query_orders_service,
    # )
    # # TODO: 实现真实的 get_supplier_capacity_info_service
    # from app.service.stock_outage.stock_outage_mock_service import (
    #     get_supplier_capacity_info_mock as get_supplier_capacity_info_service
    # )


@router.get("/random-order")
async def get_random_outage_order():
    """获取一个随机的断码订单

    Returns:
        {
            "orderId": "ORD001",
            "orderNumber": "1000000001",
            "supplierName": "东莞华美制衣厂",
            "orderCnt": 1000,
            "supplierProductionCapacity": 10,
            "supplierUsedProductionCapacity": 8,
            "skc": "sf2302287372782550"
        }
    """
    # try:
    #     # 查询所有已断码订单
    #     result = await query_orders_service(outage_type="already", days_threshold=7)
    #
    #     if not result.get("success"):
    #         return JSONResponse(
    #             status_code=500,
    #             content={"error": result.get("message", "查询订单失败")}
    #         )
    #
    #     orders = result.get("orders", [])
    #     if not orders:
    #         return JSONResponse(
    #             status_code=404,
    #             content={"error": "当前没有断码订单"}
    #         )
    #
    #     # 随机选择一个订单
    #     order = random.choice(orders)
    #
    #     # 获取供应商产能信息
    #     supplier_id = order.get("supplier_id", "SUP001")
    #     capacity_result = await get_supplier_capacity_info_service(supplier_id)
    #
    #     if not capacity_result.get("success") or not capacity_result.get("suppliers"):
    #         # 如果获取产能信息失败，使用默认值
    #         logger.warning(f"获取供应商 {supplier_id} 产能信息失败，使用默认值")
    #         total_capacity = 10
    #         used_capacity = 8
    #     else:
    #         # 获取第一个供应商的产能信息
    #         supplier_data = capacity_result["suppliers"][0]
    #         total_capacity = supplier_data.get("total_capacity", 10)
    #         used_capacity = supplier_data.get("used_capacity", 8)
    #
    #     # 构造响应数据
    #     data = RandomOrderData(
    #         orderId=order.get("order_id"),
    #         orderNumber=order.get("order_number"),
    #         supplierName=order.get("supplier_name"),
    #         orderCnt=order.get("required_quantity"),
    #         supplierProductionCapacity=total_capacity,
    #         supplierUsedProductionCapacity=used_capacity,
    #         skc=order.get("skc")
    #     )
    #
    #     return JSONResponse(content=data.model_dump())
    #
    # except Exception as e:
    #     logger.error(f"获取随机断码订单失败: {e}", exc_info=True)
    #     return JSONResponse(
    #         status_code=500,
    #         content={"error": f"服务器内部错误: {str(e)}"}
    #     )

    return JSONResponse(
                status_code=200,
                content={"error": f"OK"}
            )


@router.post("/transfer-supplier")
async def transfer_to_supplier():
    """转供应商

    将订单转移到新供应商，解决原供应商无法交付的问题。

    Returns:
        {
            "new_order_id": "ORD001_TRANSFER_20240101120000",
            "original_order_id": "ORD001",
            "status": "pending_confirmation",
            "created_at": "2024-01-01 10:00:00"
        }
    """
    logger.info("API: transfer_to_supplier called")

    # from datetime import datetime
    # data = TransferOrderData(
    #     new_order_id=f"ORD001_TRANSFER_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    #     original_order_id="ORD001",
    #     status="pending_confirmation",
    #     created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # )
    # return JSONResponse(content=data.model_dump())

    return JSONResponse(
        status_code=200,
        content={"error": f"OK"}
    )

@router.post("/update-schedule")
async def update_schedule():
    """更新供应商生产计划

    协调订单优先级，为高优先级订单插队，将低优先级订单延期。

    Returns:
        {
            "schedule_updated": true,
            "priority_order_start_date": "2024-01-03",
            "priority_order_completion_date": "2024-01-05",
            "delayed_orders_count": 2,
            "notification_sent": true
        }
    """
    logger.info("API: update_schedule called")

    # from datetime import datetime, timedelta
    # data = UpdateProductionScheduleData(
    #     schedule_updated=True,
    #     priority_order_start_date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
    #     priority_order_completion_date=(datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
    #     delayed_orders_count=2,
    #     notification_sent=True
    # )
    # return JSONResponse(content=data.model_dump())

    return JSONResponse(
        status_code=200,
        content={"error": f"OK"}
    )


@router.post("/record-exception")
async def record_exception():
    """记录异常处理

    记录无法自动解决的异常情况，等待人工处理。

    Returns:
        {
            "record_id": "EXC20240101120000",
            "order_id": "ORD001",
            "recorded_at": "2024-01-01 10:00:00"
        }
    """
    logger.info("API: record_exception called")

    # from datetime import datetime
    # data = RecordExceptionData(
    #     record_id=f"EXC{datetime.now().strftime('%Y%m%d%H%M%S')}",
    #     order_id="ORD001",
    #     recorded_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # )
    # return JSONResponse(content=data.model_dump())

    return JSONResponse(
        status_code=200,
        content={"error": f"OK"}
    )
