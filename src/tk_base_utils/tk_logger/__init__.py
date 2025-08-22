"""temp3 - 基于logging的日志程序

提供全局唯一的logger和装饰器方式的日志记录功能。
"""

from .logger import get_logger, reload_logger, reset_logger, MultiInstanceLogger
from .decorators import logger_wrapper, logger_wrapper_multi
from .config import set_logger_config_path, get_logger_config
from .levels import (
    get_log_level, get_level_name, register_custom_levels,
    is_custom_level, get_custom_levels, get_all_levels,
    CUSTOM_LOG_LEVELS, ALL_LOG_LEVELS
)

__version__ = "0.1.3"
__all__ = ["get_logger", 
           "reload_logger",
           "reset_logger", 
           "MultiInstanceLogger",
           "logger_wrapper", 
           "logger_wrapper_multi",
           "set_logger_config_path",
           "get_logger_config",
           # 日志等级管理
           "get_log_level",
           "get_level_name",
           "register_custom_levels",
           "is_custom_level",
           "get_custom_levels",
           "get_all_levels",
           "CUSTOM_LOG_LEVELS",
           "ALL_LOG_LEVELS"]
