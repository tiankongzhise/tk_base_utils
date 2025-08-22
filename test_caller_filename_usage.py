#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试caller_filename_only在logger_wrapper_multi中的使用
验证use_absolute_path配置是否正确影响日志中的文件名显示
"""

import os
import sys
import tempfile
import logging
import tomllib
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tk_base_utils.tk_logger import get_logger
from tk_base_utils.tk_logger.config import set_logger_config_path, get_logger_config
from tk_base_utils.tk_logger.decorators import logger_wrapper_multi


def create_temp_config(log_file_path: str, use_absolute_path: bool) -> str:
    """
    创建临时配置文件
    """
    config_content = f"""[logging]
name = "test_logger"
level = "DEBUG"
format = "%(asctime)s - %(name)s - %(levelname)s - [%(caller_filename)s:%(caller_lineno)d] - %(message)s"
file_path = "{log_file_path.replace(chr(92), chr(92)+chr(92))}"
max_bytes = 10485760
backup_count = 5
rotation_type = "size"
rotation_interval = "midnight"
use_absolute_path = {str(use_absolute_path).lower()}
multi_instance_shared_log = false
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False, encoding='utf-8') as temp_config:
        temp_config.write(config_content)
        return temp_config.name


def test_caller_filename_usage():
    """
    测试caller_filename_only在不同配置下的使用
    """
    print("=== 测试caller_filename_only的使用 ===")
    
    # 创建临时日志文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as temp_log:
        temp_log_path = temp_log.name
    
    temp_config_false = None
    temp_config_true = None
    
    try:
        # 测试1: use_absolute_path = False (默认值，应该使用文件名)
        print("\n1. 测试 use_absolute_path = False (使用文件名)")
        
        temp_config_false = create_temp_config(temp_log_path, False)
        set_logger_config_path(temp_config_false)
        
        logger_false = get_logger("multi", "test_false")
        
        @logger_wrapper_multi(logger_false, level='INFO')
        def test_function_false():
            return "test result"
        
        # 调用函数触发日志记录
        result = test_function_false()
        
        # 读取日志内容
        with open(temp_log_path, 'r', encoding='utf-8') as f:
            log_content_false = f.read()
        
        print(f"日志内容 (use_absolute_path=False):")
        print(log_content_false)
        
        # 检查是否使用了文件名而不是绝对路径
        filename_only = os.path.basename(__file__)
        if filename_only in log_content_false and __file__ not in log_content_false:
            print(f"✓ 正确使用了文件名: {filename_only}")
        else:
            print(f"✗ 未正确使用文件名，可能仍在使用绝对路径")
        
        # 清空日志文件
        open(temp_log_path, 'w').close()
        
        # 测试2: use_absolute_path = True (应该使用绝对路径)
        print("\n2. 测试 use_absolute_path = True (使用绝对路径)")
        
        temp_config_true = create_temp_config(temp_log_path, True)
        set_logger_config_path(temp_config_true)
        
        logger_true = get_logger("multi", "test_true")
        
        @logger_wrapper_multi(logger_true, level='INFO')
        def test_function_true():
            return "test result"
        
        # 调用函数触发日志记录
        result = test_function_true()
        
        # 读取日志内容
        with open(temp_log_path, 'r', encoding='utf-8') as f:
            log_content_true = f.read()
        
        print(f"日志内容 (use_absolute_path=True):")
        print(log_content_true)
        
        # 检查是否使用了绝对路径
        if __file__ in log_content_true:
            print(f"✓ 正确使用了绝对路径: {__file__}")
        else:
            print(f"✗ 未正确使用绝对路径")
        
        # 测试3: 验证配置的动态切换
        print("\n3. 测试配置动态切换")
        
        # 重新设置为False
        temp_config_switch = create_temp_config(temp_log_path, False)
        set_logger_config_path(temp_config_switch)
        
        # 清空日志文件
        open(temp_log_path, 'w').close()
        
        logger_switch = get_logger("multi", "test_switch")
        
        @logger_wrapper_multi(logger_switch, level='INFO')
        def test_function_switch():
            return "test result"
        
        result = test_function_switch()
        
        # 读取日志内容
        with open(temp_log_path, 'r', encoding='utf-8') as f:
            log_content_switch = f.read()
        
        print(f"日志内容 (动态切换到use_absolute_path=False):")
        print(log_content_switch)
        
        # 检查是否正确切换到文件名
        if filename_only in log_content_switch and __file__ not in log_content_switch:
            print(f"✓ 动态切换成功，正确使用了文件名: {filename_only}")
        else:
            print(f"✗ 动态切换失败")
        
        # 清理临时配置文件
        try:
            os.unlink(temp_config_switch)
        except:
            pass
            
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_log_path)
        except:
            pass
        try:
            if temp_config_false:
                os.unlink(temp_config_false)
        except:
            pass
        try:
            if temp_config_true:
                os.unlink(temp_config_true)
        except:
            pass
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_caller_filename_usage()