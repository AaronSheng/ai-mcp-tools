"""断码订单相关请求模型

定义断码订单相关 HTTP API 的请求参数模型。
"""

from typing import List, Literal
from pydantic import BaseModel, Field


class TransferOrderRequest(BaseModel):
    """转供应商请求"""
    order_id: str = Field(..., description="订单号")
    new_supplier_id: str = Field(..., description="新供应商ID")
    quantity: int = Field(..., description="转移数量", gt=0)
    reason: str = Field(..., description="转移原因")


class ContactMaterialDepartmentRequest(BaseModel):
    """面料加急请求"""
    order_id: str = Field(..., description="订单号")
    material_type: Literal["fabric", "accessory", "other"] = Field(..., description="物料类型")
    urgency: Literal["urgent", "high", "normal"] = Field(..., description="紧急程度")


class UpdateProductionScheduleRequest(BaseModel):
    """更新生产计划请求"""
    supplier_id: str = Field(..., description="供应商ID")
    priority_order_id: str = Field(..., description="优先订单号")
    delayed_order_ids: List[str] = Field(..., description="延期订单号列表")
    delay_days: int = Field(..., description="延期天数", gt=0)


class RecordExceptionRequest(BaseModel):
    """异常处理记录请求"""
    order_id: str = Field(..., description="订单号")
    supplier_id: str = Field(..., description="供应商ID")
    exception_type: str = Field(..., description="异常类型")
    exception_detail: str = Field(..., description="异常详情")
    handler_name: str = Field(..., description="处理人姓名")