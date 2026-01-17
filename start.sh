#!/bin/bash

# MCP Server 启动脚本
# 用于启动 streamable-http 模式的 MCP 服务器

echo "正在启动 MCP 服务器..."
echo "传输模式: streamable-http"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 如果脚本位于项目根目录下，则进入项目目录
if [ -f "$SCRIPT_DIR/app/main.py" ]; then
    cd "$SCRIPT_DIR"
elif [ -f "./app/main.py" ]; then
    cd .
else
    echo "错误: 未找到 app/main.py 文件，请确保在正确的项目目录中运行此脚本"
    exit 1
fi

# 检查 Python 环境
if ! command -v python &>/dev/null; then
    echo "错误: 未找到 Python 解释器"
    exit 1
fi

# 启动 MCP 服务器
echo "执行命令: python -m app.main --transport streamable-http"
python -m app.main --transport streamable-http

# 检查退出状态
if [ $? -eq 0 ]; then
    echo "MCP 服务器已成功启动"
else
    echo "MCP 服务器启动失败"
    exit 1
fi