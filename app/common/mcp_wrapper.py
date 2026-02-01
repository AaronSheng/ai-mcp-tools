
"""FastMCP 包装器 - 支持配置 base URL

用于解决反向代理环境下的 endpoint 路径问题。
"""

import os
from typing import Optional
from app.common.logging import get_logger

logger = get_logger(__name__)

def configure_mcp_base_url(mcp_instance, base_url: Optional[str] = None):
    """配置 MCP Server 的 base URL

    通过 monkey patch 修改 FastMCP 返回的 endpoint URL，
    使其包含反向代理的路径前缀。

    Args:
        mcp_instance: FastMCP 实例
        base_url: 完整的 base URL

    """
    if not base_url:
        logger.info("No base URL configured, using default")
        return

    base_url = base_url.rstrip('/')
    logger.info(f"Configuring MCP base URL: {base_url}")

    # 方法1：通过环境变量（如果 FastMCP 支持）
    os.environ['MCP_BASE_URL'] = base_url

    # 方法2：Monkey patch FastMCP 的 endpoint 返回
    # 注意：这取决于 FastMCP 的具体实现
    try:
        # 保存原始方法
        if hasattr(mcp_instance, '_get_endpoint_url'):
            original_get_endpoint = mcp_instance._get_endpoint_url

            def patched_get_endpoint(path: str = "/") -> str:
                """返回包含 base URL 的完整 endpoint"""
                if path.startswith('/'):
                    return f"{base_url}{path}"
                return f"{base_url}/{path}"

            mcp_instance._get_endpoint_url = patched_get_endpoint
            logger.info("Successfully patched MCP endpoint URL method")

    except Exception as e:
        logger.warning(f"Could not patch MCP endpoint method: {e}")
        logger.warning("Falling back to environment variable configuration")

    return mcp_instance


def get_sse_endpoint_url(base_url: Optional[str] = None, host: str = "localhost", port: int = 8008) -> dict:
    """获取 SSE 模式的 endpoint URLs

    Args:
        base_url: 完整的 base URL
        host: 主机地址
        port: 端口

    Returns:
        {
            "sse_endpoint": "http://scaip.biz.dotfashion.cn/mcp/sse",
            "messages_endpoint": "http://scaip.biz.dotfashion.cn/mcp/messages"
        }
    """
    if base_url:
        base_url = base_url.rstrip('/')
        return {
            "sse_endpoint": f"{base_url}/sse",
            "messages_endpoint": f"{base_url}/messages"
        }
    else:
        return {
            "sse_endpoint": f"http://{host}:{port}/sse",
            "messages_endpoint": f"http://{host}:{port}/messages"
        }
