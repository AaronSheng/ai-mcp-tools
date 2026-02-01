"""Python MCP Service - 应用主入口

MCP 服务器入口文件，提供 Model Context Protocol 协议支持。

支持的传输方式:
1. stdio - 通过标准输入输出与 Claude Desktop 等 AI 助手集成
2. sse - 通过 HTTP Server-Sent Events 提供远程访问
3. streamable-http - HTTP 流式传输（推荐）

注意：HTTP RESTful API 已移至 app/api 目录，需要单独启动。
"""

import sys
import argparse
from app.common.logging import get_logger

logger = get_logger("app.main")


def main():
    """主入口函数 - 启动 MCP 服务器"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="MCP Server")
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse", "streamable-http"],
        default="streamable-http",
        help="传输方式: stdio (标准输入输出), sse (Server-Sent Events), 或 streamable-http (HTTP 流式传输)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="SSE 模式下的监听地址 (默认使用配置文件中的 app_host)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="SSE 模式下的监听端口 (默认使用配置文件中的 app_port)"
    )

    args = parser.parse_args()

    logger.info(f"Starting MCP Server with transport: {args.transport}")

    try:
        # 导入所有 MCP 工具确保工具被注册
        from app.mcp import mcp
        import app.mcp.query_supplier_order
        import app.mcp.get_current_time
        from app.common.config import settings
        from app.common.mcp_wrapper import configure_mcp_base_url, get_sse_endpoint_url

        # 确定监听地址和端口
        host = args.host or settings.app.app_host
        port = args.port or settings.app.app_port

        logger.info(
            "MCP Server initialized",
            service_name=f"{settings.app.app_name}",
            version=settings.app.app_version,
            transport=args.transport
        )

        # 根据传输方式启动服务器
        if args.transport == "sse":
            # 配置 MCP base URL（如果设置了的话）
            if settings.app.mcp_base_url:
                configure_mcp_base_url(mcp, settings.app.mcp_base_url)
                endpoints = get_sse_endpoint_url(settings.app.mcp_base_url, host, port)
            else:
                endpoints = get_sse_endpoint_url(None, host, port)

            logger.info(f"Starting MCP SSE server")
            logger.info(f"SSE endpoint: {endpoints['sse_endpoint']}")
            logger.info(f"Messages endpoint: {endpoints['messages_endpoint']}")
            logger.info("Note: SSE requires dual connections (SSE + POST)")

            # 启动 SSE 服务器
            mcp.run(transport="sse", host=host, port=port)
        elif args.transport == "streamable-http":
            logger.info(f"Starting MCP Streamable HTTP server on http://{host}:{port}")
            logger.info(f"MCP endpoint: http://{host}:{port}/mcp")
            logger.info("Note: Streamable HTTP uses a single HTTP connection with streaming")

            # 创建 MCP 的 HTTP 应用
            # app = mcp.http_app(transport="streamable-http")
            mcp.run(transport="streamable-http", host=host, port=port)

            # # 挂载额外的 HTTP API 路由
            # try:
            #     from fastapi import FastAPI
            #     from app.api import api_router
            #
            #     # 创建 FastAPI 子应用
            #     api_app = FastAPI(
            #         title=f"{settings.app.app_name} - API",
            #         version=settings.app.app_version
            #     )
            #     api_app.include_router(api_router)
            #
            #     # 添加健康检查（直接在主应用上）
            #     from starlette.responses import JSONResponse as StarletteJSONResponse
            #     from starlette.requests import Request
            #
            #     async def health_check(request: Request):
            #         return StarletteJSONResponse({
            #             "status": "ok",
            #             "service": settings.app.app_name,
            #             "version": settings.app.app_version,
            #             "mode": "hybrid (MCP + HTTP)"
            #         })
            #
            #     app.add_route("/health", health_check, methods=["GET"])
            #
            #     # 挂载 FastAPI 应用（使用 /api）
            #     app.mount("/api", api_app)
            #
            #     logger.info("✅ HTTP API routes registered successfully")
            #     logger.info(f"  - Health Check: http://{host}:{port}/health")
            #
            # except Exception as e:
            #     logger.error(f"Failed to register HTTP routes: {e}", exc_info=True)
            #     logger.warning("Starting MCP server without HTTP API routes")
            #
            # # 使用 uvicorn 启动应用
            # import uvicorn
            # import asyncio
            #
            # # 配置 uvicorn，禁用 uvloop 以兼容 PyCharm 运行环境
            # config = uvicorn.Config(
            #     app=app,
            #     host=host,
            #     port=port,
            #     log_level="info",
            #     loop="none"  # 禁用自动选择事件循环
            # )
            # server = uvicorn.Server(config)
            #
            # # 使用标准 asyncio 运行
            # asyncio.run(server.serve())
        else:
            logger.info("Starting MCP stdio server")
            logger.info("Use this mode with Claude Desktop or other MCP clients")

            # 启动 stdio 服务器
            mcp.run()

    except ImportError as e:
        print("Failed to import MCP server:", e)
        # logger.error(f"Failed to import MCP server: {e}")
        sys.exit(1)
    except Exception as e:
        print("Failed to import MCP server:", e)
        # logger.error(f"Failed to start MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()