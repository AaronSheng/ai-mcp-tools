"""MCP 服务器创建和生命周期管理模块

负责 MCP 服务器的创建、配置和生命周期管理:
- MCP 服务器实例创建
- OpenTracing 初始化与关闭
- 日志系统集成
"""

import os
from app.common.logging import get_logger
from app.common.config import settings

logger = get_logger(__name__)

# 全局 tracer 实例
_global_tracer = None


def _init_tracing():
    """初始化 OpenTracing

    Returns:
        tracer 实例或 None
    """
    try:
        from app.common.tracing import setup_tracing, tracing_available

        if not tracing_available:
            logger.warning("OpenTracing not available - tracing disabled")
            return None

    except ImportError:
        logger.warning("OpenTracing dependencies not found - tracing disabled")
        return None

    # 配置 tracer
    tracer_config = {
        'sampler': {
            'type': 'probabilistic',
            'param': 0.5,
        },
        'logging': True,
        'local_agent': {
            'reporting_host': os.getenv('JAEGER_AGENT_HOST', 'localhost'),
            'reporting_port': int(os.getenv('JAEGER_AGENT_PORT', '6831')),
        }
    }

    try:
        logger.info("Initializing OpenTracing...")
        # 延迟导入配置，避免循环导入
        from app.common.config import settings
        tracer = setup_tracing(
            service_name=settings.app.app_name,
            config=tracer_config
        )

        if tracer:
            logger.info("OpenTracing initialized successfully")
            return tracer
        else:
            logger.warning("OpenTracing initialization returned None")
            return None

    except Exception as e:
        logger.warning(f"Failed to initialize OpenTracing: {e}")
        return None


def _register_tracer_cleanup(tracer):
    """注册 tracer 清理函数

    Args:
        tracer: tracer 实例
    """
    # from app.common.tracing import close_tracing
    #
    # def cleanup_tracer():
    #     logger.info("Closing OpenTracing...")
    #     close_tracing(tracer)
    #     logger.info("OpenTracing closed")
    #
    # atexit.register(cleanup_tracer)


def setup_mcp_lifecycle():
    """设置 MCP 服务生命周期管理

    初始化 tracing 等组件，并注册关闭时的清理函数
    """
    global _global_tracer

    logger.info("Initializing MCP service lifecycle...")

    # 初始化 OpenTracing
    _global_tracer = _init_tracing()

    # 如果成功初始化，注册清理函数
    if _global_tracer:
        _register_tracer_cleanup(_global_tracer)

    logger.info("MCP service lifecycle initialized")


def create_mcp():
    """创建 MCP 服务器实例

    Returns:
        配置好的 FastMCP 实例
    """
    try:
        from fastmcp import FastMCP

        mcp = FastMCP(
            name=f"{settings.app.app_name}",
            version=settings.app.app_version,
        )

        logger.info(
            "MCP Server created",
            # name=mcp.name,
            version=mcp.version
        )

        # 初始化 MCP 服务生命周期
        setup_mcp_lifecycle()

        return mcp

    except ImportError as e:
        logger.error(f"Failed to import FastMCP: {e}")
        logger.error("Please ensure fastmcp is installed: pip install fastmcp>=2.0.0")
        raise