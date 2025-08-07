"""核心日志模块

提供全局唯一的logger实例和日志配置功能。
"""

import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional
from pathlib import Path

from .config import config,set_logger_config_path


class CustomFormatter(logging.Formatter):
    """自定义格式化器，处理caller_filename和caller_lineno字段"""
    
    def format(self, record):
        # 如果记录中没有caller_filename和caller_lineno，使用默认值
        if not hasattr(record, 'caller_filename'):
            record.caller_filename = os.path.basename(record.pathname)
        if not hasattr(record, 'caller_lineno'):
            record.caller_lineno = record.lineno
        
        return super().format(record)


class SingletonLogger:
    """单例Logger类"""
    
    _instance: Optional[logging.Logger] = None
    _initialized: bool = False
    
    def __new__(cls) -> logging.Logger:
        if cls._instance is None:
            cls._instance = cls._create_logger()
            cls._initialized = True
        return cls._instance
    
    @classmethod
    def _create_logger(cls) -> logging.Logger:
        """创建logger实例"""
        logger = logging.getLogger(config.logger_name)
        
        # 避免重复添加handler
        if logger.handlers:
            return logger
        
        # 设置日志级别
        logger.setLevel(getattr(logging, config.log_level.upper(), logging.INFO))
        
        # 创建格式化器
        formatter = CustomFormatter(config.log_format)
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 添加文件处理器
        file_handler = cls._create_file_handler(formatter)
        if file_handler:
            logger.addHandler(file_handler)
        
        # 防止日志传播到根logger
        logger.propagate = False
        
        return logger
    
    @classmethod
    def _create_file_handler(cls, formatter: logging.Formatter) -> Optional[logging.Handler]:
        """创建文件处理器"""
        try:
            # 确保日志目录存在
            log_dir = os.path.dirname(config.log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # 根据轮转类型创建不同的处理器
            if config.rotation_type.lower() == "time":
                handler = TimedRotatingFileHandler(
                    filename=config.log_file_path,
                    when=config.rotation_interval,
                    backupCount=config.backup_count,
                    encoding='utf-8'
                )
            else:  # size轮转
                handler = RotatingFileHandler(
                    filename=config.log_file_path,
                    maxBytes=config.max_bytes,
                    backupCount=config.backup_count,
                    encoding='utf-8'
                )
            
            handler.setFormatter(formatter)
            return handler
            
        except Exception as e:
            print(f"警告: 创建文件处理器失败 {e}，将只使用控制台输出")
            return None
    
    @classmethod
    def reset(cls) -> None:
        """重置logger实例（主要用于测试）"""
        if cls._instance:
            # 关闭所有处理器
            for handler in cls._instance.handlers[:]:
                handler.close()
                cls._instance.removeHandler(handler)
        cls._instance = None
        cls._initialized = False


def get_logger() -> logging.Logger:
    """获取全局唯一的logger实例
    
    Returns:
        logging.Logger: 配置好的logger实例
    
    Example:
        >>> logger = get_logger()
        >>> logger.info("这是一条信息日志")
        >>> logger.error("这是一条错误日志")
    """
    return SingletonLogger()


def reset_logger() -> None:
    """重置logger实例
    
    主要用于测试或需要重新加载配置的场景。
    """
    SingletonLogger.reset()

def reload_logger(config_path:str|Path|None = None) -> None:
    """重新加载logger配置
    
    主要用于在运行时动态改变日志配置。
    """
    SingletonLogger.reset()
    if config_path:
        set_logger_config_path(config_path)
    print("logger配置已重新加载")
    return get_logger()
