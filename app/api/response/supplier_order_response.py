"""断码订单相关响应模型

定义断码订单相关 HTTP API 的响应模型。
"""

from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field

# 泛型数据类型
T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""
    code: int = Field(..., description="业务状态码，0表示成功，非0表示失败")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")


# ============================================================================
# 数据模型（用于 data 字段）
# ============================================================================

class RandomOrderData(BaseModel):
    """随机断码订单数据"""
    orderId: str = Field(..., description="订单号")
    orderNumber: Optional[str] = Field(None, description="纯数字订单号")
    supplierName: str = Field(..., description="供应商名称")
    orderCnt: int = Field(..., description="订单数量")
    supplierProductionCapacity: int = Field(..., description="供应商总产能")
    supplierUsedProductionCapacity: int = Field(..., description="供应商已用产能")
    skc: Optional[str] = Field(None, description="SKC 编码")


class TransferOrderData(BaseModel):
    """转供应商数据"""
    new_order_id: str = Field(..., description="新订单号")
    original_order_id: str = Field(..., description="原订单号")
    status: str = Field(..., description="状态")
    created_at: str = Field(..., description="创建时间")


class ContactMaterialDepartmentData(BaseModel):
    """面料加急数据"""
    request_id: str = Field(..., description="请求ID")
    material_dept_response: str = Field(..., description="物料部门响应")
    estimated_arrival_date: Optional[str] = Field(None, description="预计到货日期")
    can_expedite: bool = Field(..., description="是否可以加急")


class UpdateProductionScheduleData(BaseModel):
    """更新生产计划数据"""
    schedule_updated: bool = Field(..., description="计划是否更新")
    priority_order_start_date: str = Field(..., description="优先订单开始日期")
    priority_order_completion_date: str = Field(..., description="优先订单完成日期")
    delayed_orders_count: int = Field(..., description="延期订单数量")
    notification_sent: bool = Field(..., description="通知是否发送")


class RecordExceptionData(BaseModel):
    """异常记录数据"""
    record_id: str = Field(..., description="记录ID")
    order_id: str = Field(..., description="订单号")
    recorded_at: str = Field(..., description="记录时间")