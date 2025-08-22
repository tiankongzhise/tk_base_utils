#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试HttpLogger是否正确应用ClientConfig中的个性化日志设置
"""

import os
import tempfile
import logging
from pathlib import Path
from src.tk_base_utils.tk_http.config import ClientConfig
from src.tk_base_utils.tk_http.logger import HttpLogger
from logging.handlers import RotatingFileHandler

def test_log_level_setting():
    """测试日志级别设置"""
    print("\n=== 测试日志级别设置 ===")
    
    # 测试标准日志级别
    config = ClientConfig(log_level="DEBUG")
    logger = HttpLogger(config)
    assert logger.logger.level == logging.DEBUG
    print(f"✓ 标准级别 DEBUG 设置成功: {logger.logger.level}")
    
    # 测试自定义日志级别
    config = ClientConfig(log_level="INFO_UTILS")
    logger = HttpLogger(config)
    assert logger.logger.level == 12  # INFO_UTILS的级别值
    print(f"✓ 自定义级别 INFO_UTILS 设置成功: {logger.logger.level}")
    
    # 测试无效级别（应该回退到INFO）
    config = ClientConfig(log_level="INVALID_LEVEL")
    logger = HttpLogger(config)
    assert logger.logger.level == logging.INFO
    print(f"✓ 无效级别回退到 INFO: {logger.logger.level}")

def test_file_handler_creation():
    """测试文件处理器创建"""
    print("\n=== 测试文件处理器创建 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 测试普通文件处理器
        log_file1 = os.path.join(temp_dir, "test1.log")
        config1 = ClientConfig(
            log_file_path=log_file1,
            log_file_rotation_enabled=False
        )
        logger1 = HttpLogger(config1)
        
        # 检查是否添加了文件处理器
        file_handlers = [h for h in logger1.logger.handlers 
                        if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0
        print(f"✓ 普通文件处理器创建成功: {len(file_handlers)} 个")
        
        # 测试轮转文件处理器 - 使用不同的日志文件和实例
        log_file2 = os.path.join(temp_dir, "test2.log")
        expected_max_size = 2*1024*1024  # 2MB
        expected_backup_count = 7
        config2 = ClientConfig(
            log_file_path=log_file2,
            log_file_rotation_enabled=True,
            log_file_max_size=expected_max_size,
            log_file_backup_count=expected_backup_count
        )
        logger2 = HttpLogger(config2)
        
        rotating_handlers = [h for h in logger2.logger.handlers 
                           if isinstance(h, RotatingFileHandler)]
        assert len(rotating_handlers) > 0
        print(f"✓ 轮转文件处理器创建成功: {len(rotating_handlers)} 个")
        
        # 验证轮转配置
        print(f"总共找到 {len(rotating_handlers)} 个RotatingFileHandler")
        for i, handler in enumerate(rotating_handlers):
            print(f"Handler {i}: maxBytes={handler.maxBytes}, backupCount={handler.backupCount}, filename={getattr(handler, 'baseFilename', 'N/A')}")
        
        rotating_handler = rotating_handlers[0]
        print(f"实际配置: maxBytes={rotating_handler.maxBytes}, backupCount={rotating_handler.backupCount}")
        print(f"期望配置: maxBytes={expected_max_size}, backupCount={expected_backup_count}")
        print(f"ClientConfig配置: maxBytes={config2.log_file_max_size}, backupCount={config2.log_file_backup_count}")
        
        # 检查是否有我们创建的handler
        our_handler = None
        for handler in rotating_handlers:
            if hasattr(handler, 'baseFilename') and log_file2 in handler.baseFilename:
                our_handler = handler
                break
        
        if our_handler:
            print(f"找到我们创建的handler: maxBytes={our_handler.maxBytes}, backupCount={our_handler.backupCount}")
            assert our_handler.maxBytes == expected_max_size
            assert our_handler.backupCount == expected_backup_count
            print(f"✓ 轮转配置正确: maxBytes={our_handler.maxBytes}, backupCount={our_handler.backupCount}")
        else:
            print("警告：没有找到我们创建的handler，使用第一个handler进行验证")
            assert rotating_handler.maxBytes == expected_max_size
            assert rotating_handler.backupCount == expected_backup_count
            print(f"✓ 轮转配置正确: maxBytes={rotating_handler.maxBytes}, backupCount={rotating_handler.backupCount}")

def test_no_duplicate_handlers():
    """测试不会重复添加处理器"""
    print("\n=== 测试不重复添加处理器 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, "test.log")
        
        config = ClientConfig(log_file_path=log_file)
        logger = HttpLogger(config)
        
        initial_handler_count = len(logger.logger.handlers)
        
        # 再次调用配置应用方法
        logger._apply_config_settings()
        
        final_handler_count = len(logger.logger.handlers)
        assert initial_handler_count == final_handler_count
        print(f"✓ 不会重复添加处理器: {initial_handler_count} -> {final_handler_count}")

def test_directory_creation():
    """测试自动创建日志目录"""
    print("\n=== 测试自动创建日志目录 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建一个不存在的子目录路径
        log_dir = os.path.join(temp_dir, "logs", "http")
        log_file = os.path.join(log_dir, "test.log")
        
        assert not os.path.exists(log_dir)
        
        config = ClientConfig(log_file_path=log_file)
        logger = HttpLogger(config)
        
        # 验证目录被创建
        assert os.path.exists(log_dir)
        print(f"✓ 日志目录自动创建成功: {log_dir}")

def test_logging_functionality():
    """测试日志功能是否正常工作"""
    print("\n=== 测试日志功能 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, "test.log")
        
        config = ClientConfig(
            log_file_path=log_file,
            log_level="DEBUG",
            log_requests=True,
            log_responses=True
        )
        logger = HttpLogger(config)
        
        # 测试各种日志方法
        logger.log_request("GET", "https://example.com", {"User-Agent": "test"})
        logger.log_response("GET", "https://example.com", 200, {"Content-Type": "text/html"}, "OK")
        logger.log_retry("GET", "https://example.com", 1, 3, "Connection timeout")
        logger.log_error("GET", "https://example.com", "Network error")
        
        # 验证日志文件是否被创建并包含内容
        assert os.path.exists(log_file)
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "GET" in content
            assert "https://example.com" in content
            print(f"✓ 日志文件创建成功，包含 {len(content)} 个字符")

def test_config_integration():
    """测试完整的配置集成"""
    print("\n=== 测试完整配置集成 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, "integration_test.log")
        
        # 创建包含所有日志配置的ClientConfig
        config = ClientConfig(
            log_level="INFO_UTILS",
            log_requests=True,
            log_responses=True,
            log_file_path=log_file,
            log_file_max_size=512*1024,  # 512KB
            log_file_backup_count=5,
            log_file_rotation_enabled=True
        )
        
        logger = HttpLogger(config)
        
        # 验证所有配置都被正确应用
        assert logger.logger.level == 12  # INFO_UTILS
        assert logger.config.log_requests == True
        assert logger.config.log_responses == True
        
        # 验证文件处理器配置
        rotating_handlers = [h for h in logger.logger.handlers 
                           if isinstance(h, RotatingFileHandler)]
        assert len(rotating_handlers) > 0
        
        handler = rotating_handlers[0]
        assert handler.maxBytes == 512*1024
        assert handler.backupCount == 5
        
        print("✓ 所有配置都被正确应用")
        
        # 测试实际日志记录
        logger.logger.info_utils("这是一条INFO_UTILS级别的日志")
        logger.logger.debug("这是一条DEBUG级别的日志（应该不会记录）")
        
        # 验证日志文件内容
        assert os.path.exists(log_file)
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "INFO_UTILS级别的日志" in content
            assert "DEBUG级别的日志" not in content  # DEBUG级别应该被过滤
            print("✓ 日志级别过滤正常工作")

def main():
    """运行所有测试"""
    print("开始测试HttpLogger的ClientConfig个性化设置...")
    
    try:
        test_log_level_setting()
        test_file_handler_creation()
        test_no_duplicate_handlers()
        test_directory_creation()
        test_logging_functionality()
        test_config_integration()
        
        print("\n🎉 所有测试通过！HttpLogger成功应用了ClientConfig中的个性化日志设置")
        print("\n主要功能验证:")
        print("✓ 日志级别设置（标准级别和自定义级别）")
        print("✓ 文件处理器创建（普通和轮转）")
        print("✓ 日志目录自动创建")
        print("✓ 防止重复添加处理器")
        print("✓ 日志功能正常工作")
        print("✓ 完整配置集成")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()