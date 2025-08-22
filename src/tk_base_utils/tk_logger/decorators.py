"""装饰器模块

提供logger_wrapper装饰器，支持函数调用日志记录。
"""

import time
import functools
import inspect
from typing import Callable, Any,Literal

from .logger import get_logger, EnhancedLogger


MODEL_LITERAL = Literal["simple","default"]
LEVEL_LITERAL = Literal["INFO_CONFIG","INFO_UTILS","INFO_DATABASE","INFO_KERNEL","INFO_CORE","INFO_SERVICE","INFO_CONTROL","INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]

def logger_wrapper(level:LEVEL_LITERAL = "INFO",model: MODEL_LITERAL = "default") -> Callable:
    """日志装饰器
    
    这是logger_wrapper_multi的特殊形式，使用单例logger
    
    Args:
        level: 日志级别，支持 'INFO_CONFIG','INFO_UTILS','INFO_DATABASE','INFO_KERNEL','INFO_CORE','INFO_SERVICE','INFO_CONTROL','INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL'，默认为 'INFO'
        model: 日志模型，支持 'simple' 和 'default'，默认为 'default'
    
    Returns:
        装饰器函数
    
    Example:
    
    
        >>> @logger_wrapper()
        ... def add(a, b):
        ...     return a + b
        
        >>> @logger_wrapper(model='simple')
        ... def multiply(x, y):
        ...     return x * y
        
        >>> @logger_wrapper(level='DEBUG')
        ... def subtract(a, b):
        ...     return a - b
        
        >>> @logger_wrapper(level='INFO_CONFIG',model='default')
        ... def divide(a, b):
        ...     return a / b
    """
    # 获取单例logger实例
    logger = get_logger()
    # 使用logger_wrapper_multi的实现
    return logger_wrapper_multi(logger, level, model)


def logger_wrapper_multi(logger: EnhancedLogger, level: LEVEL_LITERAL = "INFO", model: MODEL_LITERAL = "default") -> Callable:
    """多例版本的日志装饰器，支持指定logger实例
    
    Args:
        logger: 指定的logger实例
        level: 日志级别，支持 'INFO_CONFIG','INFO_UTILS','INFO_DATABASE','INFO_KERNEL','INFO_CORE','INFO_SERVICE','INFO_CONTROL','INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL'，默认为 'INFO'
        model: 日志模型，支持 'simple' 和 'default'，默认为 'default'
    
    Returns:
        装饰器函数
    
    Example:
        >>> # 获取多例logger
        >>> logger1 = get_logger("multi", "instance1")
        >>> logger2 = get_logger("multi", "instance2")
        
        >>> @logger_wrapper_multi(logger1)
        ... def add(a, b):
        ...     return a + b
        
        >>> @logger_wrapper_multi(logger2, level='DEBUG', model='simple')
        ... def multiply(x, y):
        ...     return x * y
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            func_name = func.__name__
            
            # 获取调用者的文件名和行号信息
            frame = inspect.currentframe()
            try:
                # 获取调用栈，找到调用被装饰函数的位置
                caller_frame = frame.f_back  # wrapper的调用者
                caller_filename = caller_frame.f_code.co_filename
                caller_lineno = caller_frame.f_lineno
                
                # 提取文件名（不包含路径）
                import os
                caller_filename_only = os.path.basename(caller_filename)
            finally:
                del frame  # 避免循环引用
            
            # 记录开始时间
            start_time = time.time()
            start_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
            
            # 获取函数签名
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # 记录参数详情
            param_info = []
            for param_name, param_value in bound_args.arguments.items():
                if param_name == 'self':
                    # 对于self参数，显示类名和实例变量名
                    class_name = param_value.__class__.__name__
                    
                    # 尝试获取实例的变量名
                    instance_var_name = None
                    try:
                        # 获取调用栈信息
                        import linecache
                        caller_code = linecache.getline(caller_filename, caller_lineno).strip()
                        
                        # 解析调用代码，提取变量名
                        # 匹配模式：变量名.方法名( 或 变量名.方法名 (
                        import re
                        pattern = r'(\w+)\.' + re.escape(func_name) + r'\s*\('
                        match = re.search(pattern, caller_code)
                        if match:
                            instance_var_name = match.group(1)
                    except Exception:
                        # 如果获取失败，忽略错误
                        pass
                    
                    if instance_var_name:
                        param_info.append(f"{param_name}=<{class_name} instance: {instance_var_name}>")
                    else:
                        param_info.append(f"{param_name}=<{class_name} instance>")
                else:
                    param_info.append(f"{param_name}={repr(param_value)}")
            
            # 创建extra字典，包含真实的文件名和行号
            extra_info = {
                'caller_filename': caller_filename,
                'caller_lineno': caller_lineno
            }
            
            # 根据level参数获取对应的日志方法
            def get_log_method(level_name: str):
                # 使用统一的日志等级管理，动态构建方法映射
                from .levels import get_custom_levels
                
                level_methods = {
                    'DEBUG': logger.debug,
                    'INFO': logger.info,
                    'WARNING': logger.warning,
                    'ERROR': logger.error,
                    'CRITICAL': logger.critical,
                }
                
                # 动态添加自定义等级的方法映射
                custom_levels = get_custom_levels()
                for custom_level_name in custom_levels.keys():
                    method_name = custom_level_name.lower()
                    if hasattr(logger, method_name):
                        level_methods[custom_level_name] = getattr(logger, method_name)
                
                return level_methods.get(level_name.upper(), logger.info)
            
            log_method = get_log_method(level)
            
            # 根据model参数决定记录的详细程度
            if model.lower() == "default":    
                log_method(
                    f"函数调用开始 - 函数名: {func_name}, "
                    f"参数: ({', '.join(param_info)}), "
                    f"开始时间: {start_time_str}",
                    extra=extra_info
                )
            elif model.lower() == "simple":
                log_method(
                    f"函数调用开始 - 函数名: {func_name}, "
                    f"开始时间: {start_time_str}",
                    extra=extra_info
                )
            else:
                log_method(
                    f"函数调用开始 - 函数名: {func_name}, "
                    f"参数: ({', '.join(param_info)}), "
                    f"开始时间: {start_time_str}",
                    extra=extra_info
                )
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 记录结束时间和执行时间
                end_time = time.time()
                end_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
                execution_time = end_time - start_time
                

                log_method(
                    f"函数调用成功 - 函数名: {func_name}, "
                    f"返回值: {repr(result)}, "
                    f"开始时间: {start_time_str}, "
                    f"结束时间: {end_time_str}, "
                    f"执行时间: {execution_time:.4f}秒",
                    extra=extra_info
                )
            
                return result
                
            except Exception as e:
                # 记录异常信息
                end_time = time.time()
                end_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
                execution_time = end_time - start_time

                log_method(
                    f"函数调用异常 - 函数名: {func_name}, "
                    f"异常: {type(e).__name__}: {str(e)}, "
                    f"开始时间: {start_time_str}, "
                    f"结束时间: {end_time_str}, "
                    f"执行时间: {execution_time:.4f}秒",
                    extra={
                        'caller_filename': caller_filename,
                        'caller_lineno': caller_lineno
                    }
                )
            
                # 重新抛出异常
                raise
        
        return wrapper
    return decorator
