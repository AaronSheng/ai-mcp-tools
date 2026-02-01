# AI-MCP-Tools - AI Model Context Protocol 工具服务

AI-MCP-Tools 是一个基于 Model Context Protocol (MCP) 标准的工具服务框架，旨在为 AI 助手提供结构化数据访问能力。该服务实现了 MCP 协议，允许 AI 助手通过标准化接口调用各种业务工具。

## 项目目的

本项目的主要目的是：

- **提供 MCP 协议支持**：实现 Model Context Protocol 规范，使 AI 助手能够发现和调用外部工具
- **业务数据集成**：提供库存缺货等业务数据的标准化访问接口
- **工具化服务**：将业务逻辑封装为 AI 可调用的工具，提升 AI 助手的实用性
- **可扩展架构**：设计灵活的架构，支持快速添加新的业务工具

## 项目结构

```
ai-mcp-tools/
├── app/                          # 主应用程序目录
│   ├── api/                      # API 接口定义
│   │   ├── request/              # 请求模型定义
│   │   ├── response/             # 响应模型定义
│   │   └── stock_outage_api.py   # 库存缺货 API
│   ├── common/                   # 通用模块
│   │   ├── app.py               # MCP 服务器创建和生命周期管理
│   │   ├── config.py            # 应用配置管理
│   │   ├── logging.py           # 日志系统配置
│   │   └── mcp_wrapper.py       # MCP 服务包装器
│   ├── mcp/                      # MCP 协议相关模块
│   │   ├── __init__.py          # MCP 服务初始化
│   │   └── stock_outstage_tool.py # 库存缺货工具定义
│   └── main.py                   # 应用主入口
├── start_server.sh               # 服务器启动脚本
├── requirements.txt              # 项目依赖
└── README.md                     # 项目说明文档
```

### 核心模块说明

#### app/common/
- **app.py**: MCP 服务器实例创建和生命周期管理，处理循环导入问题
- **config.py**: 应用配置管理，使用 Pydantic Settings 进行配置管理
- **logging.py**: 统一日志系统配置
- **mcp_wrapper.py**: MCP 服务包装器，支持配置 base URL

#### app/mcp/
- **\_\_init\_\_.py**: MCP 服务初始化，使用延迟加载避免循环导入
- **stock_outstage_tool.py**: 定义库存相关的 MCP 工具

#### app/api/
- **request/response**: 定义 API 请求和响应的数据模型
- **stock_outage_api.py**: 提供库存缺货相关的 REST API 接口

## 功能特性

- **多传输协议支持**：支持 stdio、SSE (Server-Sent Events) 和 streamable-http 三种传输方式
- **工具注册机制**：自动注册 MCP 工具，支持动态发现
- **HTTP API 集成**：同时提供 MCP 协议和传统 HTTP API 接口
- **健康检查**：内置健康检查端点
- **日志记录**：结构化日志记录，便于监控和调试

## 快速开始

### 启动服务

使用启动脚本：
```bash
./start_server.sh
```

或直接运行：
```bash
python -m app.main --transport streamable-http
```

### 传输方式选项

- `stdio`: 标准输入输出模式，适用于 Claude Desktop 等 AI 助手
- `sse`: Server-Sent Events 模式，通过 HTTP 提供远程访问
- `streamable-http`: HTTP 流式传输模式（推荐）

## 技术栈

- **Python 3.12+**
- **FastMCP**: MCP 协议实现
- **FastAPI**: Web 框架
- **Pydantic**: 数据验证和设置管理
- **Uvicorn**: ASGI 服务器

## 设计原则

1. **模块化设计**：各组件职责清晰，便于维护和扩展
2. **循环导入解决**：通过延迟加载和动态导入解决复杂的依赖关系
3. **协议兼容**：严格遵循 MCP 协议规范
4. **可配置性**：支持多种环境配置
5. **可观测性**：完善的日志和健康检查机制