from typing import Literal, Any

from app.mcp import mcp
from app.common.logging import logger

@mcp.tool()
async def query_supplier_order(
    supplier_id: str,
    status: Literal["in_production", "pending", "all"] = "in_production"
) -> dict[str, Any]:
    """查询供应商订单 ⭐ 数据查询工具

    用于分析订单优先级，协调插队。
    查询供应商当前的所有订单，找出可以延期的低优先级订单。

    适用场景：
    - 断码原因为"产能不足"
    - 需要协调订单优先级，为断码单插队
    - 评估供应商当前产能负荷

    Args:
        supplier_id: 供应商ID
        status: 订单状态
            - in_production: 生产中
            - pending: 待生产
            - all: 全部

    Returns:
        订单列表，每个订单包含以下字段:
        [
            {
                "order_id": "订单ID",
                "product_name": "产品名称",
                "required_quantity": 1000,  # 需求数量
                "priority_score": 45.5,     # 优先级分数
                "order_created_at": "2024-01-01 10:00:00",  # 订单创建时间
                "can_be_delayed": True,     # 是否可延期（优先级<50）
                "delay_risk_level": "低"    # 延期风险：低/中/高
            }
        ]

    Examples:
        # 查询供应商在产订单，寻找可延期订单
        result = await query_supplier_order(
            supplier_id="SUP123",
            status="in_production"
        )
        # 返回示例:
        # [
        #     {
        #         "order_id": "xxx",
        #         "product_name": "xxx",
        #         "required_quantity": 1000,
        #         "priority_score": 45.5,
        #         "order_created_at": "2024-01-01 10:00:00",
        #         "can_be_delayed": True,
        #         "delay_risk_level": "低"
        #     }
        # ]
    """
    try:
        logger.info(f"MCP Tool called: query_supplier_orders (supplier_id={supplier_id})")
        # result = await query_supplier_orders_service(supplier_id, status)

        orders = [
            {
                "order_id": "S123",
                "product_name": "衬衫",
                "required_quantity": 1000,
                "priority_score": 45.5,
                "order_created_at": "2024-01-01 10:00:00",
                "can_be_delayed": True,  # 是否可延期（优先级<50）
                "delay_risk_level": "低"  # 延期风险：低/中/高
            }
        ]
        return {
            "success": True,
            "message": "查询供应商订单成功",
            "orders": orders
        }
    except Exception as e:
        logger.error(f"query_supplier_orders failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "查询供应商订单失败"
        }