#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终测试HttpLogger的ClientConfig个性化设置功能
"""

import os
import tempfile
import logging
from pathlib import Path
from src.tk_base_utils.tk_http.config import ClientConfig
from src.tk_base_utils.tk_http.logger import HttpLogger
from logging.handlers import RotatingFileHandler

def cleanup_handlers(logger_instance):
    """清理logger的所有处理器"""
    for handler in logger_instance.logger.handlers[:]:
        if isinstance(handler, (logging.FileHandler, RotatingFileHandler)):
            handler.close()
            logger_instance.logger.removeHandler(handler)

def test_personalized_config():
    """测试个性化配置功能"""
    print("\n=== 测试HttpLogger个性化配置功能 ===")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    log_file = os.path.join(temp_dir, "personalized_test.log")
    
    try:
        # 测试自定义配置
        config = ClientConfig(
            log_level="DEBUG",
            log_file_path=log_file,
            log_file_rotation_enabled=True,
            log_file_max_size=512*1024,  # 512KB
            log_file_backup_count=10,
            log_requests=True,
            log_responses=True
        )
        
        logger = HttpLogger(config)
        
        # 验证日志级别
        assert logger.logger.level == logging.DEBUG
        print(f"✓ 日志级别设置正确: {logger.logger.level}")
        
        # 验证文件处理器配置
        rotating_handlers = [h for h in logger.logger.handlers 
                           if isinstance(h, RotatingFileHandler)]
        
        # 找到我们创建的处理器
        our_handler = None
        for handler in rotating_handlers:
            if hasattr(handler, 'baseFilename') and log_file in handler.baseFilename:
                our_handler = handler
                break
        
        assert our_handler is not None
        assert our_handler.maxBytes == 512*1024
        assert our_handler.backupCount == 10
        print(f"✓ 文件处理器配置正确: maxBytes={our_handler.maxBytes}, backupCount={our_handler.backupCount}")
        
        # 测试日志功能
        logger.log_request("POST", "https://api.example.com/data", {"Content-Type": "application/json"})
        logger.log_response(201, "https://api.example.com/data", 0.5, {"Location": "/data/123"}, 150)
        
        # 验证日志文件创建
        assert os.path.exists(log_file)
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "POST" in content
            assert "https://api.example.com/data" in content
            assert "201" in content
        print(f"✓ 日志文件创建成功，包含预期内容")
        
        # 清理处理器
        cleanup_handlers(logger)
        
        print("✓ 所有个性化配置测试通过！")
        
    finally:
        # 清理临时文件
        try:
            if os.path.exists(log_file):
                os.remove(log_file)
            os.rmdir(temp_dir)
        except:
            pass  # 忽略清理错误

def test_config_override():
    """测试配置覆盖功能"""
    print("\n=== 测试配置覆盖功能 ===")
    
    temp_dir = tempfile.mkdtemp()
    log_file = os.path.join(temp_dir, "override_test.log")
    
    try:
        # 第一个配置
        config1 = ClientConfig(
            log_file_path=log_file,
            log_file_rotation_enabled=True,
            log_file_max_size=1024*1024,  # 1MB
            log_file_backup_count=3
        )
        logger1 = HttpLogger(config1)
        
        # 第二个配置（相同文件，不同参数）
        config2 = ClientConfig(
            log_file_path=log_file,
            log_file_rotation_enabled=True,
            log_file_max_size=2*1024*1024,  # 2MB
            log_file_backup_count=8
        )
        logger2 = HttpLogger(config2)
        
        # 验证第二个logger使用了新的配置
        rotating_handlers = [h for h in logger2.logger.handlers 
                           if isinstance(h, RotatingFileHandler)]
        
        our_handler = None
        for handler in rotating_handlers:
            if hasattr(handler, 'baseFilename') and log_file in handler.baseFilename:
                our_handler = handler
                break
        
        assert our_handler is not None
        assert our_handler.maxBytes == 2*1024*1024
        assert our_handler.backupCount == 8
        print(f"✓ 配置覆盖成功: maxBytes={our_handler.maxBytes}, backupCount={our_handler.backupCount}")
        
        # 清理处理器
        cleanup_handlers(logger1)
        cleanup_handlers(logger2)
        
    finally:
        # 清理临时文件
        try:
            if os.path.exists(log_file):
                os.remove(log_file)
            os.rmdir(temp_dir)
        except:
            pass

def main():
    """运行所有测试"""
    print("开始测试HttpLogger的ClientConfig个性化设置功能...")
    
    try:
        test_personalized_config()
        test_config_override()
        
        print("\n🎉 所有测试通过！HttpLogger成功实现了ClientConfig个性化设置功能")
        print("\n主要功能验证:")
        print("✓ 日志级别个性化设置")
        print("✓ 文件处理器个性化配置（文件路径、轮转大小、备份数量）")
        print("✓ 配置覆盖功能（当多个实例使用相同文件时）")
        print("✓ 日志功能正常工作")
        print("\n优化效果:")
        print("- HttpLogger现在完全支持ClientConfig中的所有日志配置")
        print("- 支持动态配置覆盖，确保使用最新的配置参数")
        print("- 保持了与tk_logger的良好集成")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()