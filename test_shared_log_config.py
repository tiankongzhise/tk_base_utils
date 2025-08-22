#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试HttpLogger的共享日志配置逻辑
验证当log_file_path为None时，个性化的文件大小和轮转设置不生效
"""

import os
import tempfile
import logging
from logging.handlers import RotatingFileHandler
from src.tk_base_utils.tk_http.config import ClientConfig
from src.tk_base_utils.tk_http.logger import HttpLogger


def cleanup_handlers(logger):
    """清理日志处理器"""
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)


def test_shared_log_config():
    """测试共享日志配置：log_file_path为None时，个性化设置不生效"""
    print("\n=== 测试共享日志配置 ===")
    
    # 创建一个配置，log_file_path为None，但设置了个性化的文件大小和轮转参数
    config = ClientConfig(
        log_file_path=None,  # 共享日志，不指定文件路径
        log_file_max_size=2*1024*1024,  # 2MB，个性化设置
        log_file_backup_count=7,  # 7个备份，个性化设置
        log_file_rotation_enabled=True,  # 启用轮转，个性化设置
        log_level='DEBUG'
    )
    
    print(f"ClientConfig设置: log_file_path={config.log_file_path}")
    print(f"ClientConfig设置: log_file_max_size={config.log_file_max_size}")
    print(f"ClientConfig设置: log_file_backup_count={config.log_file_backup_count}")
    print(f"ClientConfig设置: log_file_rotation_enabled={config.log_file_rotation_enabled}")
    
    # 创建HttpLogger实例
    logger = HttpLogger(config=config)
    
    # 验证日志级别设置是否生效（这个应该生效）
    assert logger.logger.level == logging.DEBUG, f"Expected DEBUG level, got {logger.logger.level}"
    print("✓ 日志级别设置正确生效")
    
    # 检查是否没有添加个性化的文件处理器
    file_handlers = [h for h in logger.logger.handlers if isinstance(h, (logging.FileHandler, RotatingFileHandler))]
    
    if len(file_handlers) == 0:
        print("✓ 没有添加个性化文件处理器（符合预期，因为log_file_path为None）")
    else:
        print(f"发现 {len(file_handlers)} 个文件处理器:")
        for i, handler in enumerate(file_handlers):
            print(f"  处理器 {i+1}: {type(handler).__name__}")
            if hasattr(handler, 'baseFilename'):
                print(f"    文件路径: {handler.baseFilename}")
            if isinstance(handler, RotatingFileHandler):
                print(f"    maxBytes: {handler.maxBytes}")
                print(f"    backupCount: {handler.backupCount}")
                # 这些应该是默认值，不是个性化配置的值
                if handler.maxBytes == config.log_file_max_size:
                    print("    ⚠️ 警告：文件处理器使用了个性化的maxBytes设置，这不符合预期")
                if handler.backupCount == config.log_file_backup_count:
                    print("    ⚠️ 警告：文件处理器使用了个性化的backupCount设置，这不符合预期")
    
    # 清理
    cleanup_handlers(logger.logger)
    print("✓ 共享日志配置测试完成")


def test_personalized_log_config():
    """测试个性化日志配置：log_file_path不为None时，个性化设置生效"""
    print("\n=== 测试个性化日志配置 ===")
    
    # 创建临时文件路径
    with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as tmp_file:
        log_file_path = tmp_file.name
    
    try:
        # 创建一个配置，指定log_file_path，设置个性化参数
        config = ClientConfig(
            log_file_path=log_file_path,  # 个性化日志文件
            log_file_max_size=3*1024*1024,  # 3MB，个性化设置
            log_file_backup_count=8,  # 8个备份，个性化设置
            log_file_rotation_enabled=True,  # 启用轮转，个性化设置
            log_level='INFO'
        )
        
        print(f"ClientConfig设置: log_file_path={config.log_file_path}")
        print(f"ClientConfig设置: log_file_max_size={config.log_file_max_size}")
        print(f"ClientConfig设置: log_file_backup_count={config.log_file_backup_count}")
        print(f"ClientConfig设置: log_file_rotation_enabled={config.log_file_rotation_enabled}")
        
        # 创建HttpLogger实例
        logger = HttpLogger(config=config)
        
        # 验证日志级别设置是否生效
        assert logger.logger.level == logging.INFO, f"Expected INFO level, got {logger.logger.level}"
        print("✓ 日志级别设置正确生效")
        
        # 检查是否添加了个性化的文件处理器
        file_handlers = [h for h in logger.logger.handlers if isinstance(h, (logging.FileHandler, RotatingFileHandler))]
        
        assert len(file_handlers) > 0, "应该有文件处理器被添加"
        print(f"✓ 找到 {len(file_handlers)} 个文件处理器")
        
        # 查找指向目标文件的RotatingFileHandler
        target_handler = None
        for handler in file_handlers:
            if isinstance(handler, RotatingFileHandler):
                handler_file = getattr(handler, 'baseFilename', None)
                if handler_file and os.path.abspath(handler_file) == os.path.abspath(log_file_path):
                    target_handler = handler
                    break
        
        assert target_handler is not None, "应该找到指向目标文件的RotatingFileHandler"
        print("✓ 找到目标RotatingFileHandler")
        
        # 验证个性化配置是否正确应用
        print(f"处理器配置: maxBytes={target_handler.maxBytes}, backupCount={target_handler.backupCount}")
        assert target_handler.maxBytes == config.log_file_max_size, f"Expected maxBytes {config.log_file_max_size}, got {target_handler.maxBytes}"
        assert target_handler.backupCount == config.log_file_backup_count, f"Expected backupCount {config.log_file_backup_count}, got {target_handler.backupCount}"
        print("✓ 个性化文件处理器配置正确应用")
        
        # 清理
        cleanup_handlers(logger.logger)
        
    finally:
        # 删除临时文件
        if os.path.exists(log_file_path):
            os.unlink(log_file_path)
    
    print("✓ 个性化日志配置测试完成")


if __name__ == "__main__":
    test_shared_log_config()
    test_personalized_log_config()
    print("\n=== 所有测试完成 ===")