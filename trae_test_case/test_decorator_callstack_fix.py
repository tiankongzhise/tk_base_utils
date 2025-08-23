#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试装饰器调用栈修复
验证logger_wrapper和logger_wrapper_multi是否能正确获取被装饰函数的调用位置
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tk_base_utils.tk_logger import get_logger
from tk_base_utils.tk_logger.config import set_logger_config_path
from tk_base_utils.tk_logger.decorators import logger_wrapper, logger_wrapper_multi


def create_temp_config(log_file_path: str) -> str:
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
use_absolute_path = false
multi_instance_shared_log = false
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False, encoding='utf-8') as temp_config:
        temp_config.write(config_content)
        return temp_config.name


@logger_wrapper(level='INFO')
def test_function_with_logger_wrapper():
    """使用logger_wrapper装饰的测试函数"""
    return "result from logger_wrapper"


def test_function_with_logger_wrapper_multi():
    """使用logger_wrapper_multi装饰的测试函数"""
    return "result from logger_wrapper_multi"


def test_decorator_callstack_fix():
    """
    测试装饰器调用栈修复
    """
    print("=== 测试装饰器调用栈修复 ===")
    
    # 创建临时日志文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as temp_log:
        temp_log_path = temp_log.name
    
    temp_config = None
    
    try:
        # 设置配置
        temp_config = create_temp_config(temp_log_path)
        set_logger_config_path(temp_config)
        
        current_filename = os.path.basename(__file__)
        
        # 测试1: logger_wrapper装饰器
        print("\n1. 测试 logger_wrapper 装饰器")
        
        # 调用被装饰的函数 - 这一行应该被记录为调用位置
        result1 = test_function_with_logger_wrapper()  # 这是第67行
        
        # 读取日志内容
        with open(temp_log_path, 'r', encoding='utf-8') as f:
            log_content1 = f.read()
        
        print(f"日志内容 (logger_wrapper):")
        print(log_content1)
        
        # 检查是否正确记录了当前文件和行号
        expected_line = "67"  # 调用test_function_with_logger_wrapper的行号
        if current_filename in log_content1 and expected_line in log_content1:
            print(f"✓ logger_wrapper正确记录了调用位置: {current_filename}:{expected_line}")
        else:
            print(f"✗ logger_wrapper未正确记录调用位置")
            if "decorators.py" in log_content1:
                print(f"  错误：记录了decorators.py的位置而不是调用位置")
        
        # 清空日志文件
        open(temp_log_path, 'w').close()
        
        # 测试2: logger_wrapper_multi装饰器
        print("\n2. 测试 logger_wrapper_multi 装饰器")
        
        # 获取logger实例并装饰函数
        logger = get_logger("multi", "test_instance")
        decorated_func = logger_wrapper_multi(logger, level='INFO')(test_function_with_logger_wrapper_multi)
        
        # 调用被装饰的函数 - 这一行应该被记录为调用位置
        result2 = decorated_func()  # 这是第90行
        
        # 读取日志内容
        with open(temp_log_path, 'r', encoding='utf-8') as f:
            log_content2 = f.read()
        
        print(f"日志内容 (logger_wrapper_multi):")
        print(log_content2)
        
        # 检查是否正确记录了当前文件和行号
        expected_line2 = "90"  # 调用decorated_func的行号
        if current_filename in log_content2 and expected_line2 in log_content2:
            print(f"✓ logger_wrapper_multi正确记录了调用位置: {current_filename}:{expected_line2}")
        else:
            print(f"✗ logger_wrapper_multi未正确记录调用位置")
            if "decorators.py" in log_content2:
                print(f"  错误：记录了decorators.py的位置而不是调用位置")
        
        # 测试3: 嵌套调用情况
        print("\n3. 测试嵌套调用情况")
        
        def nested_caller():
            """嵌套调用函数"""
            return test_function_with_logger_wrapper()  # 这应该记录nested_caller的位置
        
        # 清空日志文件
        open(temp_log_path, 'w').close()
        
        result3 = nested_caller()
        
        # 读取日志内容
        with open(temp_log_path, 'r', encoding='utf-8') as f:
            log_content3 = f.read()
        
        print(f"日志内容 (嵌套调用):")
        print(log_content3)
        
        # 检查是否正确记录了nested_caller内部的调用位置
        if current_filename in log_content3 and "nested_caller" not in log_content3:
            print(f"✓ 嵌套调用正确记录了调用位置")
        else:
            print(f"✗ 嵌套调用未正确记录调用位置")
            
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_log_path)
        except:
            pass
        try:
            if temp_config:
                os.unlink(temp_config)
        except:
            pass
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_decorator_callstack_fix()