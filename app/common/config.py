"""应用配置管理模块

使用Pydantic Settings进行配置管理，支持环境变量和.env文件
"""

import os
from typing import List, Optional, Dict, Any
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    """应用基础配置"""
    model_config = SettingsConfigDict(
        env_file=os.getenv("DOTENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # 应用配置
    app_sys_name: str = Field(default="ai-demo-server", description="系统名称")
    app_name: str = Field(default="ai-demo-server", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    app_env: str = Field(default="test", description="运行环境")
    app_debug: bool = Field(default=True, description="调试模式")
    app_host: str = Field(default="0.0.0.0", description="监听地址")
    app_port: int = Field(default=8000, description="监听端口")
    app_secret_key: str = Field(default="your-secret-key-here", description="应用密钥")

    # MCP 服务配置
    mcp_base_url: Optional[str] = Field(default=None,description="MCP 服务的完整基础URL（如 http://mcp.cn/mcp）")
    mcp_base_path: str = Field(default="", description="MCP 服务的基础路径前缀（如 /mcp）")

    # Mock 数据配置
    use_mock_data: bool = Field(default=False, description="是否使用 Mock 数据（文件模式），适用于无数据库环境")

    # 数据库配置
    # database_url: str = Field(default="sqlite:///./data/app.db", description="数据库连接")
    # database_pool_size: int = Field(default=10, description="连接池大小")
    # database_pool_timeout: int = Field(default=30, description="连接超时")
    # database_pool_recycle: int = Field(default=3600, description="连接回收时间")
    # database_echo: bool = Field(default=False, description="SQL日志")

    # 判断当前环境是否为测试环境
    @property
    def is_test(self) -> bool:
        return self.app_env == "test"

    # 判断当前环境是否为生产环境
    @property
    def is_production(self) -> bool:
        return self.app_env == "prod"


###################### 日志配置 ######################
class LogSettings(BaseSettings):
    """日志配置"""
    model_config = SettingsConfigDict(
        env_file=os.getenv("DOTENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="json", description="日志格式")
    log_file_enabled: bool = Field(default=True, description="文件日志开关")
    log_file_path: str = Field(default="logs/app.log", description="日志文件路径")
    log_file_max_size: str = Field(default="10MB", description="日志文件最大大小")
    log_file_backup_count: int = Field(default=5, description="日志文件备份数量")
    log_console_enabled: bool = Field(default=True, description="控制台日志开关")
    log_console_simple_format: bool = Field(default=False, description="控制台简单格式开关")
    log_structured: bool = Field(default=True, description="结构化日志")


class SecuritySettings(BaseSettings):
    """安全配置"""
    model_config = SettingsConfigDict(
        env_file=os.getenv("DOTENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    jwt_secret_key: str = Field(default="your-jwt-secret-key-here", description="JWT密钥")
    jwt_algorithm: str = Field(default="HS256", description="JWT算法")
    jwt_access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间")
    jwt_refresh_token_expire_days: int = Field(default=7, description="刷新令牌过期时间")


class MonitoringSettings(BaseSettings):
    """监控配置"""
    model_config = SettingsConfigDict(
        env_file=os.getenv("DOTENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    monitoring_enabled: bool = Field(default=True, description="监控开关")
    metrics_enabled: bool = Field(default=True, description="指标开关")
    metrics_path: str = Field(default="/metrics", description="指标路径")
    health_check_path: str = Field(default="/health", description="健康检查路径")
    health_check_detailed_path: str = Field(default="/health/detailed", description="详细健康检查路径")


class ApsSettings(BaseSettings):
    """APS配置"""
    model_config = SettingsConfigDict(
        env_file=os.getenv("DOTENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    aps_config_path: str = Field(default="../../../../config/aps_config.yaml", description="健康检查路径")


class Settings:
    """全局配置管理器"""

    def __init__(self):
        self.app = AppSettings()
        self.log = LogSettings()
        self.security = SecuritySettings()
        self.monitoring = MonitoringSettings()
        self.aps = ApsSettings()


# 全局配置实例
settings = Settings()