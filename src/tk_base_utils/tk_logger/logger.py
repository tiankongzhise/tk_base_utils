"""核心日志模块

提供全局唯一的logger实例和日志配置功能。"""

import os
import logging
import inspect
from abc import ABC, abstractmethod
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional, Dict, Union
from pathlib import Path

from .config import config,set_logger_config_path


class EnhancedLogger(logging.Logger):
    """增强的Logger类，提供自定义日志级别方法和IDE代码提示支持"""
    
    def _log_with_caller_info(self, level, msg, *args, **kwargs):
        """带调用者信息的日志记录方法"""
        if self.isEnabledFor(level):
            # 获取调用者信息
            frame = inspect.currentframe()
            try:
                # 跳过当前方法和调用的自定义日志方法，找到真正的调用者
                caller_frame = frame.f_back.f_back
                caller_filename_full = caller_frame.f_code.co_filename
                caller_lineno = caller_frame.f_lineno
                
                # 根据配置选择使用绝对路径或相对路径
                if config.use_absolute_path:
                    caller_filename = caller_filename_full
                else:
                    caller_filename = os.path.basename(caller_filename_full)
                
                # 添加调用者信息到extra中
                if 'extra' not in kwargs:
                    kwargs['extra'] = {}
                kwargs['extra']['caller_filename'] = caller_filename
                kwargs['extra']['caller_lineno'] = caller_lineno
                
            finally:
                del frame
            
            self._log(level, msg, args, **kwargs)
    
    def info_config(self, msg, *args, **kwargs):
        """记录INFO_CONFIG级别的日志"""
        self._log_with_caller_info(11, msg, *args, **kwargs)
    
    def info_utils(self, msg, *args, **kwargs):
        """记录INFO_UTILS级别的日志"""
        self._log_with_caller_info(12, msg, *args, **kwargs)
    
    def info_database(self, msg, *args, **kwargs):
        """记录INFO_DATABASE级别的日志"""
        self._log_with_caller_info(13, msg, *args, **kwargs)
    
    def info_kernel(self, msg, *args, **kwargs):
        """记录INFO_KERNEL级别的日志"""
        self._log_with_caller_info(14, msg, *args, **kwargs)
    
    def info_core(self, msg, *args, **kwargs):
        """记录INFO_CORE级别的日志"""
        self._log_with_caller_info(15, msg, *args, **kwargs)
    
    def info_service(self, msg, *args, **kwargs):
        """记录INFO_SERVICE级别的日志"""
        self._log_with_caller_info(16, msg, *args, **kwargs)
    
    def info_control(self, msg, *args, **kwargs):
        """记录INFO_CONTROL级别的日志"""
        self._log_with_caller_info(17, msg, *args, **kwargs)


class CustomFormatter(logging.Formatter):
    """自定义格式化器，处理caller_filename和caller_lineno字段"""
    
    def format(self, record):
        # 如果记录中没有caller_filename和caller_lineno，使用默认值
        if not hasattr(record, 'caller_filename'):
            if config.use_absolute_path:
                record.caller_filename = record.pathname
            else:
                record.caller_filename = os.path.basename(record.pathname)
        if not hasattr(record, 'caller_lineno'):
            record.caller_lineno = record.lineno
        
        return super().format(record)


class BaseLogger(ABC):
    """Logger基类，提取单例和多例的公共功能"""
    
    @classmethod
    def _enhance_logger(cls) -> None:
        """增强logger实例，注册自定义日志级别"""
        # 注册自定义日志级别名称
        logging.addLevelName(11, "INFO_CONFIG")
        logging.addLevelName(12, "INFO_UTILS")
        logging.addLevelName(13, "INFO_DATABASE")
        logging.addLevelName(14, "INFO_KERNEL")
        logging.addLevelName(15, "INFO_CORE")
        logging.addLevelName(16, "INFO_SERVICE")
        logging.addLevelName(17, "INFO_CONTROL")
    
    @classmethod
    def _setup_logger_level(cls, logger: EnhancedLogger) -> None:
        """设置logger的日志级别"""
        level_name = config.log_level.upper()
        # 首先尝试获取标准日志级别
        level = getattr(logging, level_name, None)
        if level is None:
            # 如果不是标准级别，尝试通过级别名称获取自定义级别
            level_mapping = {
                'INFO_CONFIG': 11,
                'INFO_UTILS': 12,
                'INFO_DATABASE': 13,
                'INFO_KERNEL': 14,
                'INFO_CORE': 15,
                'INFO_SERVICE': 16,
                'INFO_CONTROL': 17
            }
            level = level_mapping.get(level_name, logging.INFO)
        logger.setLevel(level)
    
    @classmethod
    def _create_console_handler(cls, formatter: logging.Formatter) -> logging.Handler:
        """创建控制台处理器"""
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        return console_handler
    
    @classmethod
    def _create_file_handler_base(cls, formatter: logging.Formatter, log_file_path: str) -> Optional[logging.Handler]:
        """创建文件处理器的基础方法"""
        try:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # 根据轮转类型创建不同的处理器
            if config.rotation_type.lower() == "time":
                handler = TimedRotatingFileHandler(
                    filename=log_file_path,
                    when=config.rotation_interval,
                    backupCount=config.backup_count,
                    encoding='utf-8'
                )
            else:  # size轮转
                handler = RotatingFileHandler(
                    filename=log_file_path,
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
    def _setup_logger_handlers(cls, logger: EnhancedLogger, formatter: logging.Formatter, log_file_path: str) -> None:
        """设置logger的处理器"""
        # 避免重复添加handler
        if logger.handlers:
            return
        
        # 添加控制台处理器
        console_handler = cls._create_console_handler(formatter)
        logger.addHandler(console_handler)
        
        # 添加文件处理器
        file_handler = cls._create_file_handler_base(formatter, log_file_path)
        if file_handler:
            logger.addHandler(file_handler)
        
        # 防止日志传播到根logger
        logger.propagate = False
    
    @abstractmethod
    def _create_logger_instance(self, *args, **kwargs) -> EnhancedLogger:
        """创建logger实例的抽象方法，由子类实现"""
        pass
    
    @abstractmethod
    def reset(self, *args, **kwargs) -> None:
        """重置logger实例的抽象方法，由子类实现"""
        pass


class SingletonLogger(BaseLogger):
    """单例Logger类"""
    
    _instance: Optional[EnhancedLogger] = None
    _initialized: bool = False
    
    def __new__(cls) -> EnhancedLogger:
        if cls._instance is None:
            cls._instance = cls._create_logger()
            cls._initialized = True
        return cls._instance
    
    @classmethod
    def _create_logger(cls) -> EnhancedLogger:
        """创建logger实例"""
        cls._enhance_logger()
        # 设置自定义Logger类
        logging.setLoggerClass(EnhancedLogger)
        logger = logging.getLogger(config.logger_name)
        # 恢复默认Logger类
        logging.setLoggerClass(logging.Logger)
        
        # 设置日志级别
        cls._setup_logger_level(logger)
        
        # 创建格式化器
        formatter = CustomFormatter(config.log_format)
        
        # 设置处理器
        cls._setup_logger_handlers(logger, formatter, config.log_file_path)
        
        return logger
    
    def _create_logger_instance(self, *args, **kwargs) -> EnhancedLogger:
        """实现抽象方法"""
        return self._create_logger()

    
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

    

class MultiInstanceLogger(BaseLogger):
    """多例Logger管理类"""
    
    _instances: Dict[str, EnhancedLogger] = {}
    _initialized_instances: Dict[str, bool] = {}
    
    @classmethod
    def get_logger(cls, instance_name: str) -> EnhancedLogger:
        """获取指定名称的logger实例（兼容方法名）"""
        return cls.get_instance(instance_name)
    
    @classmethod
    def get_instance(cls, instance_name: str) -> EnhancedLogger:
        """获取指定名称的logger实例
        
        Args:
            instance_name: 实例名称
            
        Returns:
            EnhancedLogger: 指定名称的logger实例
        """
        if instance_name not in cls._instances:
            cls._instances[instance_name] = cls._create_logger(instance_name)
            cls._initialized_instances[instance_name] = True
        return cls._instances[instance_name]
    
    @classmethod
    def _create_logger(cls, instance_name: str) -> EnhancedLogger:
        """创建指定名称的logger实例"""
        cls._enhance_logger()
        # 设置自定义Logger类
        logging.setLoggerClass(EnhancedLogger)
        logger = logging.getLogger(f"{config.logger_name}_{instance_name}")
        # 恢复默认Logger类
        logging.setLoggerClass(logging.Logger)
        
        # 设置日志级别
        cls._setup_logger_level(logger)
        
        # 创建格式化器
        formatter = CustomFormatter(config.log_format)
        
        # 根据配置决定日志文件路径
        if config.multi_instance_shared_log:
            # 共享同一个日志文件
            log_file_path = config.log_file_path
        else:
            # 为每个实例创建独立的日志文件
            base_path = Path(config.log_file_path)
            log_file_path = str(base_path.parent / f"{base_path.stem}_{instance_name}{base_path.suffix}")
        
        # 设置处理器
        cls._setup_logger_handlers(logger, formatter, log_file_path)
        
        return logger
    
    def _create_logger_instance(self, instance_name: str) -> EnhancedLogger:
        """实现抽象方法"""
        return self._create_logger(instance_name)
    
    def reset(self) -> None:
        """重置所有logger实例"""
        for logger in self._loggers.values():
            # 移除所有处理器
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
                handler.close()
        self._loggers.clear()
    
    @classmethod
    def _enhance_logger(cls) -> None:
        """增强logger实例，注册自定义日志级别"""
        # 注册自定义日志级别名称
        logging.addLevelName(11, "INFO_CONFIG")
        logging.addLevelName(12, "INFO_UTILS")
        logging.addLevelName(13, "INFO_DATABASE")
        logging.addLevelName(14, "INFO_KERNEL")
        logging.addLevelName(15, "INFO_CORE")
        logging.addLevelName(16, "INFO_SERVICE")
        logging.addLevelName(17, "INFO_CONTROL")
    

    
    @classmethod
    def get_instances(cls) -> Dict[str, EnhancedLogger]:
        """获取所有实例的字典"""
        return cls._instances.copy()
    
    @property
    def instances(self) -> Dict[str, EnhancedLogger]:
        """获取所有实例的字典（实例方法）"""
        return self.__class__._instances.copy()
    
    @classmethod
    def reset(cls, instance_name: Optional[str] = None) -> None:
        """重置logger实例
        
        Args:
            instance_name: 要重置的实例名称，如果为None则重置所有实例
        """
        if instance_name is None:
            # 重置所有实例
            for name, logger in cls._instances.items():
                # 关闭所有处理器
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)
            cls._instances.clear()
            cls._initialized_instances.clear()
        else:
            # 重置指定实例
            if instance_name in cls._instances:
                logger = cls._instances[instance_name]
                # 关闭所有处理器
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)
                del cls._instances[instance_name]
                del cls._initialized_instances[instance_name]


def get_logger(mode: str = "singleton", instance_name: str = "default") -> EnhancedLogger:
    """获取logger实例
    
    Args:
        mode: 模式选择，"singleton" 返回单例，"multi" 返回多例，默认为 "singleton"
        instance_name: 当mode为"multi"时的实例名称，默认为"default"
    
    Returns:
        EnhancedLogger: 配置好的增强logger实例，支持自定义日志级别方法
    
    Example:
        >>> # 获取单例logger
        >>> logger = get_logger()
        >>> logger.info("这是一条信息日志")
        
        >>> # 获取多例logger
        >>> logger1 = get_logger("multi", "instance1")
        >>> logger2 = get_logger("multi", "instance2")
        >>> logger1.info("实例1的日志")
        >>> logger2.info("实例2的日志")
    """
    if mode.lower() == "multi":
        return MultiInstanceLogger.get_instance(instance_name)
    else:
        return SingletonLogger()


def reset_logger(instance_name: str = None) -> None:
    """重置logger实例
    
    Args:
        instance_name: logger实例名称
                      - None: 重置单例logger（默认行为）
                      - "ALL": 重置单例和所有多例实例
                      - 其他字符串: 重置指定名称的多例实例
    
    主要用于测试或需要重新加载配置的场景。
    """
    if instance_name is None:
        # 默认重置单例
        SingletonLogger.reset()
    elif instance_name.upper() == "ALL":
        # 重置所有实例
        SingletonLogger.reset()
        MultiInstanceLogger.reset()
    else:
        # 重置指定的多例实例
        if instance_name in MultiInstanceLogger._instances:
            MultiInstanceLogger.reset(instance_name)
        else:
            # 实例不存在，输出警告
            temp_logger = logging.getLogger("temp_warning")
            temp_logger.warning(f"Logger实例 '{instance_name}' 不存在，无法重置")

def reload_logger(config_path: str|Path|None = None, instance_name: str = None) -> Optional[EnhancedLogger]:
    """重新加载logger配置
    
    Args:
        config_path: 新的配置文件路径，如果为None则使用当前配置
        instance_name: logger实例名称
                      - None: 重载单例logger（默认行为）
                      - "ALL": 重载单例和所有多例实例
                      - 其他字符串: 重载指定名称的多例实例
    
    Returns:
        EnhancedLogger: 重载后的logger实例，如果实例不存在则返回None
    
    主要用于在运行时动态改变日志配置。
    """
    # 更新配置文件路径
    if config_path:
        set_logger_config_path(config_path)
    
    if instance_name is None:
        # 默认重载单例
        SingletonLogger.reset()
        print("单例logger配置已重新加载")
        return get_logger()
    elif instance_name.upper() == "ALL":
        # 重载所有实例
        SingletonLogger.reset()
        MultiInstanceLogger.reset()
        print("所有logger实例配置已重新加载")
        return get_logger()
    else:
        # 重载指定的多例实例
        if instance_name in MultiInstanceLogger._instances:
            MultiInstanceLogger.reset(instance_name)
            print(f"Logger实例 '{instance_name}' 配置已重新加载")
            return get_logger("multi", instance_name)
        else:
            # 实例不存在，输出警告并返回None
            temp_logger = logging.getLogger("temp_warning")
            temp_logger.warning(f"Logger实例 '{instance_name}' 不存在，无法重载")
            return None

