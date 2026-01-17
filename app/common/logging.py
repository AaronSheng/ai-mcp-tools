"""日志管理模块

使用公司标准日志SDK实现结构化日志，支持:
- JSON格式输出
- 文件轮转
- 全链路追踪ID
- 结构化字段
"""

import json
import logging
import os
import sys
from contextvars import ContextVar
from types import FrameType
from typing import Dict, Any, Optional, List, cast

from loguru import logger

from app.common.config import settings

# 全链路追踪ID
_trace_id: ContextVar[str] = ContextVar('x_trace_id', default="")


class TraceID:
    @staticmethod
    def set_trace(id: str, title: str = "task") -> ContextVar[str]:
        """设置全链路追踪ID
        Args:
            id: 追踪ID
            title: 追踪任务标题
        Returns:
            ContextVar[str]: 追踪ID上下文变量
        """
        id = f"{id}"
        _trace_id.set(id)
        return _trace_id

    @staticmethod
    def get_trace() -> str:
        """获取当前追踪ID
        Returns:
            str: 当前追踪ID
        """
        return _trace_id.get()


# 环境变量
env_dict = {
    'service': os.getenv('serviceName', settings.app.app_name)
}

def serialize(record):
    """序列化日志记录为JSON格式"""
    subset = {
        "timestamp": record["time"].strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "+0800",
        "message": record["message"],
        "level": record["level"].name,
        "traceID": _trace_id.get(),
        "thread": f"{record['thread'].name}-{record['thread'].id}",
    }

    # 添加环境变量
    subset.update(env_dict)

    # 添加额外字段
    if "extra" in record and isinstance(record["extra"], dict):
        for key, value in record["extra"].items():
            if key != "serialized" and key not in subset:
                subset[key] = value

    return json.dumps(subset)


def json_format(record):
    """将日志输出格式化为json格式"""
    record["extra"]["serialized"] = serialize(record)
    return "{extra[serialized]}\n"


def simple_format(record):
    """简单格式化日志输出，适合开发调试"""
    # 使用loguru的标准格式化方式
    name = record.get("extra", {}).get("name", "")
    if name:
        return "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[name]: <30} | {message}\n"
    else:
        return "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}\n"


def _logger_filter_info_only(record):
    """过滤只显示INFO级别日志"""
    return record["level"].name == "INFO"


def _logger_filter_error_only(record):
    """过滤只显示ERROR级别日志"""
    return record["level"].name == "ERROR"


def _logger_filter_warn_only(record):
    """过滤只显示WARNING级别日志"""
    return record["level"].name == "WARNING"


def init_log_path(log_path):
    """初始化日志目录"""
    if not os.path.exists(log_path):
        os.makedirs(log_path, exist_ok=True)


def _configure_logger():
    """配置loguru日志器"""
    # 移除默认处理器
    logger.remove()

    # 创建日志目录
    log_path = os.environ.get("LOG_FILE_PATH") or settings.log.log_file_path
    parent_dir = os.path.dirname(log_path)
    init_log_path(parent_dir)

    # 根据配置选择日志格式
    file_format = json_format if settings.log.log_format.lower() == "json" else simple_format
    console_format = simple_format if settings.log.log_console_simple_format else json_format

    # 配置INFO级别的日志文件
    logger.add(
        os.path.join(parent_dir, "INFO.{time:YYYY-MM-DD}.log"),
        level="INFO",
        rotation="00:00",
        retention="5 days",
        enqueue=True,
        filter=_logger_filter_info_only,
        format=file_format,
        watch=True
    )

    # 配置WARN级别的日志文件
    logger.add(
        os.path.join(parent_dir, "WARN.{time:YYYY-MM-DD}.log"),
        level="WARNING",
        rotation="00:00",
        retention="5 days",
        enqueue=True,
        filter=_logger_filter_warn_only,
        format=file_format,
        watch=True
    )

    # 配置ERROR级别的日志文件
    logger.add(
        os.path.join(parent_dir, "ERROR.{time:YYYY-MM-DD}.log"),
        level="ERROR",
        rotation="00:00",
        retention="5 days",
        enqueue=True,
        filter=_logger_filter_error_only,
        format=file_format,
        watch=True
    )

    # 控制台输出 - 调试模式使用简单格式，生产模式使用JSON格式
    if settings.log.log_console_enabled:
        logger.add(sys.stderr, format=console_format)


class InterceptHandler(logging.Handler):
    """拦截Python标准日志并重定向到loguru"""

    def emit(self, record: logging.LogRecord) -> None:
        # 获取对应的loguru级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # 查找调用源
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage(),
        )


def init_logger(logger_names=None):
    """初始化日志系统，将Python标准日志重定向到loguru
    Args:
        logger_names: 需要重定向的日志器名称列表
    """
    # 配置loguru
    _configure_logger()

    # 设置默认的日志器名称列表，包括常用的库
    if logger_names is None:
        logger_names = [
            "uvicorn",
            "uvicorn.error",
            "uvicorn.access",
            "fastapi",
            "starlette",
            "gunicorn",
            "gunicorn.error",
            "gunicorn.access",
            "kafka",
            "consul",
        ]

    # 重定向所有指定的日志器
    for logger_name in logger_names:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False


class LoggerMixin:
    """日志混入类，提供类级别的logger属性"""

    @property
    def logger(self):
        """获取当前类的日志器"""
        return get_logger(self.__class__.__name__)


def get_logger(name: str = None):
    """获取日志器
    Args:
        name: 日志器名称，默认为调用模块名
    Returns:
        loguru日志器实例
    """
    return logger.bind(name=name)


def log_request(request_id: str, method: str, path: str, **kwargs):
    """记录请求日志"""
    TraceID.set_trace(request_id)
    logger.info(
        "HTTP Request",
        request_id=request_id,
        method=method,
        path=path,
        **kwargs
    )


def log_response(request_id: str, status_code: int, duration: float, **kwargs):
    """记录响应日志"""
    logger.info(
        "HTTP Response",
        request_id=request_id,
        status_code=status_code,
        duration_ms=round(duration * 1000, 2),
        **kwargs
    )


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None, **kwargs):
    """记录错误日志"""
    logger.error(
        f"Error occurred: {str(error)}",
        error_type=error.__class__.__name__,
        context=context or {},
        **kwargs
    )


def log_performance(operation: str, duration: float, **kwargs):
    """记录性能日志"""
    logger.info(
        "Performance Metric",
        operation=operation,
        duration_ms=round(duration * 1000, 2),
        **kwargs
    )


# 初始化日志系统
init_logger()