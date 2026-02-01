from datetime import datetime
from typing import Dict, Any

from app.mcp import mcp
from app.common.logging import logger

@mcp.tool()
async def get_current_time() -> Dict[str, Any]:
    """获取当前时间 ⭐ 时间工具

    返回当前服务器的日期和时间信息。
    适用于需要获取精确时间戳或当前日期的场景。

    Returns:
        包含当前时间信息的字典:
        {
            "current_time": "2024-01-17 14:30:45",
            "timestamp": 1705478445.123456,
            "formatted_date": "2024-01-17",
            "formatted_time": "14:30:45",
            "timezone": "Asia/Shanghai"
        }

    Examples:
        # 获取当前时间
        time_info = await get_current_time()
    """

    try:
        current_datetime = datetime.now()
        logger.info(f"MCP Tool called: get_current_time")

        result = {
            "current_time": current_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": current_datetime.timestamp(),
            "formatted_date": current_datetime.strftime("%Y-%m-%d"),
            "formatted_time": current_datetime.strftime("%H:%M:%S"),
            "timezone": "Asia/Shanghai"  # 可根据实际需要修改
        }

        return result
    except Exception as e:
        logger.error(f"get_current_time failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "获取当前时间失败"
        }