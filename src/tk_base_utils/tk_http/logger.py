"""HTTP客户端日志管理"""

import time
from typing import Dict, Any, Optional
from .config import ClientConfig
from ..tk_logger import get_logger


class HttpLogger:
    """HTTP客户端日志管理器"""
    
    def __init__(self, config: ClientConfig):
        self.config = config
        # 使用tk_logger的多例功能创建logger实例
        # 使用唯一的实例名称避免冲突
        instance_name = f"http_client_{id(self)}"
        self.logger = get_logger("multi", instance_name)
    
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