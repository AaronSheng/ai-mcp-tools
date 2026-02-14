"""MCP Package - MCP 适配器包

统一创建和管理 MCP 服务器实例。
所有 MCP 工具文件应从此处导入 mcp 实例。
"""

from app.common.app import create_mcp

mcp = create_mcp()

__all__ = ["mcp"]
