"""HTTP客户端日志管理"""

import time
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Optional
from pathlib import Path
from .config import ClientConfig
from ..tk_logger import get_logger
from ..tk_logger.levels import get_log_level


class HttpLogger:
    """HTTP客户端日志管理器"""
    
    def __init__(self, config: ClientConfig):
        self.config = config
        # 使用tk_logger的多例功能创建logger实例
        # 使用唯一的实例名称避免冲突
        instance_name = f"http_client_{id(self)}"
        self.logger = get_logger("multi", instance_name)
        
        # 应用ClientConfig中的个性化日志设置
        self._apply_config_settings()
    
    def log_request(self, method: str, url: str, headers: Optional[Dict[str, str]] = None, 
                   data: Any = None) -> None:
        """记录请求日志"""
        if not self.config.log_requests:
            return
        
        log_data = {
            "type": "request",
            "method": method,
            "url": url,
            "timestamp": time.time()
        }
        
        if headers:
            # 过滤敏感信息
            safe_headers = self._filter_sensitive_headers(headers)
            log_data["headers"] = safe_headers
        
        if data:
            log_data["data"] = str(data)[:500]  # 限制数据长度
        
        self.logger.info_utils(f"Request: {method} {url}")
        self.logger.info_utils(f"Request details: {log_data}")
    
    def log_response(self, status_code: int, url: str, elapsed: float, 
                    headers: Optional[Dict[str, str]] = None, 
                    content_length: Optional[int] = None) -> None:
        """记录响应日志"""
        if not self.config.log_responses:
            return
        
        log_data = {
            "type": "response",
            "status_code": status_code,
            "url": url,
            "elapsed": elapsed,
            "timestamp": time.time()
        }
        
        if headers:
            safe_headers = self._filter_sensitive_headers(headers)
            log_data["headers"] = safe_headers
        
        if content_length is not None:
            log_data["content_length"] = content_length
        
        if 200 <= status_code < 400:
            self.logger.info_utils(f"Response: {status_code} {url} ({elapsed:.3f}s)")
        else:
            self.logger.warning(f"Response: {status_code} {url} ({elapsed:.3f}s)")
        self.logger.info_utils(f"Response details: {log_data}")
    
    def log_retry(self, attempt: int, max_retries: int, delay: float, 
                 error: Exception, url: str) -> None:
        """记录重试日志"""
        self.logger.warning(
            f"Retry {attempt}/{max_retries} for {url} after {delay:.1f}s delay. "
            f"Error: {type(error).__name__}: {error}"
        )
    
    def log_error(self, error: Exception, url: str, method: str) -> None:
        """记录错误日志"""
        self.logger.error(
            f"Error in {method} {url}: {type(error).__name__}: {error}"
        )
    
    def log_timeout(self, url: str, method: str, timeout: float) -> None:
        """记录超时日志"""
        self.logger.warning(
            f"Timeout ({timeout}s) for {method} {url}"
        )
    
    def log_connection_error(self, url: str, method: str, error: Exception) -> None:
        """记录连接错误日志"""
        self.logger.warning(
            f"Connection error for {method} {url}: {error}"
        )
    
    def _filter_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """过滤敏感的请求头信息"""
        sensitive_keys = {
            'authorization', 'cookie', 'x-api-key', 'x-auth-token',
            'x-access-token', 'bearer', 'api-key', 'auth-token'
        }
        
        filtered = {}
        for key, value in headers.items():
            if key.lower() in sensitive_keys:
                filtered[key] = "***REDACTED***"
            else:
                filtered[key] = value
        
        return filtered
    
    def _apply_config_settings(self) -> None:
        """应用ClientConfig中的个性化日志设置"""
        # 设置日志级别
        self._set_log_level()
        
        # 只有当配置了日志文件路径时，才应用个性化的文件处理器设置
        # log_file_path为None表示使用共享日志，不应用个性化的文件大小和轮转设置
        if self.config.log_file_path:
            self._add_file_handler()
    
    def _set_log_level(self) -> None:
        """设置日志级别"""
        if self.config.log_level is None:
            return
        
        level_name = self.config.log_level.upper()
        
        # 使用统一的日志等级管理模块获取等级数值
        level = get_log_level(level_name, logging.INFO)
        
        self.logger.setLevel(level)
    
    def _add_file_handler(self) -> None:
        """添加个性化文件处理器
        
        注意：此方法只在log_file_path不为None时调用，用于创建个性化的文件处理器。
        当log_file_path为None时，表示使用共享日志，不会调用此方法，
        个性化的log_file_max_size、log_file_backup_count、log_file_rotation_enabled设置不会生效。
        """
        try:
            # 确保日志目录存在
            log_dir = os.path.dirname(self.config.log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # 检查是否已经有指向相同文件的处理器
            target_file_handler = None
            for handler in self.logger.handlers:
                if isinstance(handler, (logging.FileHandler, RotatingFileHandler)):
                    handler_file = getattr(handler, 'baseFilename', None)
                    if handler_file and os.path.abspath(handler_file) == os.path.abspath(self.config.log_file_path):
                        target_file_handler = handler
                        break
            
            if target_file_handler is None:
                # 没有找到指向目标文件的处理器，创建新的个性化处理器
                if self.config.log_file_rotation_enabled:
                    # 使用个性化配置的RotatingFileHandler
                    file_handler = RotatingFileHandler(
                        filename=self.config.log_file_path,
                        maxBytes=self.config.log_file_max_size,
                        backupCount=self.config.log_file_backup_count,
                        encoding='utf-8'
                    )
                else:
                    # 使用普通FileHandler，不进行轮转
                    file_handler = logging.FileHandler(
                        filename=self.config.log_file_path,
                        encoding='utf-8'
                    )
                
                # 设置格式化器
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            else:
                # 找到了指向目标文件的处理器，检查是否需要更新配置
                if isinstance(target_file_handler, RotatingFileHandler):
                    # 如果现有的是RotatingFileHandler，检查个性化配置是否匹配
                    if (target_file_handler.maxBytes != self.config.log_file_max_size or 
                        target_file_handler.backupCount != self.config.log_file_backup_count):
                        # 个性化配置不匹配，移除旧的处理器，添加新的
                        self.logger.removeHandler(target_file_handler)
                        target_file_handler.close()
                        
                        if self.config.log_file_rotation_enabled:
                            new_handler = RotatingFileHandler(
                                filename=self.config.log_file_path,
                                maxBytes=self.config.log_file_max_size,
                                backupCount=self.config.log_file_backup_count,
                                encoding='utf-8'
                            )
                        else:
                            new_handler = logging.FileHandler(
                                filename=self.config.log_file_path,
                                encoding='utf-8'
                            )
                        
                        formatter = logging.Formatter(
                            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                        )
                        new_handler.setFormatter(formatter)
                        self.logger.addHandler(new_handler)
                
        except Exception as e:
            # 如果个性化文件handler创建失败，记录警告但不影响程序运行
            self.logger.warning(f"Failed to create personalized file handler for {self.config.log_file_path}: {e}")
