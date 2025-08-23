#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试create_logger_wrapper函数的功能

验证create_logger_wrapper创建的装饰器与logger_wrapper功能完全一致，
但使用指定的logger实例而不是单例logger实例。
"""

import sys
import os
import tempfile
import time

# 添加src路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tk_base_utils.tk_logger.decorators import create_logger_wrapper, logger_wrapper
from tk_base_utils.tk_logger.logger import get_logger
from tk_base_utils.tk_logger.config import set_logger_config_path

def create_temp_config(use_absolute_path=False):
    """创建临时配置文件"""
    config_content = f"""
[logger]
use_absolute_path = {str(use_absolute_path).lower()}
log_level = "DEBUG"
log_format = "[%(asctime)s] [%(levelname)s] [%(caller_filename)s:%(caller_lineno)d] %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

[file_handler]
enable = true
log_file = "test_create_logger_wrapper.log"
max_bytes = 10485760
backup_count = 5

[console_handler]
enable = true
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False, encoding='utf-8') as f:
        f.write(config_content)
        return f.name

def test_create_logger_wrapper():
    """测试create_logger_wrapper函数"""
    print("=== 测试create_logger_wrapper功能 ===")
    
    # 设置测试配置
    config_path = create_temp_config(use_absolute_path=False)
    try:
        set_logger_config_path(config_path)
        
        # 创建自定义logger实例
        custom_logger = get_logger("multi", "test_instance")
        
        # 使用create_logger_wrapper创建装饰器
        my_logger_wrapper = create_logger_wrapper(custom_logger)
        
        # 定义测试函数
        @my_logger_wrapper()
        def test_function_default(a, b):
            """使用默认参数的测试函数"""
            return a + b
        
        @my_logger_wrapper(level='DEBUG', model='simple')
        def test_function_simple(x, y):
            """使用simple模式的测试函数"""
            return x * y
        
        @my_logger_wrapper(level='INFO_CONFIG', model='default')
        def test_function_config(value):
            """使用INFO_CONFIG级别的测试函数"""
            return value ** 2
        
        # 执行测试
        print("\n1. 测试默认参数装饰器:")
        result1 = test_function_default(3, 5)
        print(f"   结果: {result1}")
        
        print("\n2. 测试simple模式装饰器:")
        result2 = test_function_simple(4, 6)
        print(f"   结果: {result2}")
        
        print("\n3. 测试INFO_CONFIG级别装饰器:")
        result3 = test_function_config(7)
        print(f"   结果: {result3}")
        
        # 测试异常处理
        @my_logger_wrapper(level='ERROR')
        def test_function_exception():
            """测试异常处理的函数"""
            raise ValueError("测试异常")
        
        print("\n4. 测试异常处理:")
        try:
            test_function_exception()
        except ValueError as e:
            print(f"   捕获异常: {e}")
        
        print("\n✅ create_logger_wrapper功能测试完成")
        
    finally:
        # 清理临时配置文件
        if os.path.exists(config_path):
            os.unlink(config_path)

def test_comparison_with_logger_wrapper():
    """对比create_logger_wrapper与logger_wrapper的行为"""
    print("\n=== 对比create_logger_wrapper与logger_wrapper ===")
    
    # 设置测试配置
    config_path = create_temp_config(use_absolute_path=False)
    try:
        set_logger_config_path(config_path)
        
        # 创建自定义logger实例
        custom_logger = get_logger("multi", "comparison_test")
        my_logger_wrapper = create_logger_wrapper(custom_logger)
        
        # 定义对比测试函数
        @logger_wrapper()
        def original_wrapper_func(a, b):
            """使用原始logger_wrapper的函数"""
            return a + b
        
        @my_logger_wrapper()
        def custom_wrapper_func(a, b):
            """使用create_logger_wrapper的函数"""
            return a + b
        
        print("\n1. 使用原始logger_wrapper:")
        result1 = original_wrapper_func(10, 20)
        print(f"   结果: {result1}")
        
        print("\n2. 使用create_logger_wrapper:")
        result2 = custom_wrapper_func(10, 20)
        print(f"   结果: {result2}")
        
        print("\n✅ 对比测试完成 - 两者行为应该一致，只是使用不同的logger实例")
        
    finally:
        # 清理临时配置文件
        if os.path.exists(config_path):
            os.unlink(config_path)

def test_multiple_logger_instances():
    """测试多个logger实例的独立性"""
    print("\n=== 测试多个logger实例的独立性 ===")
    
    # 设置测试配置
    config_path = create_temp_config(use_absolute_path=False)
    try:
        set_logger_config_path(config_path)
        
        # 创建多个不同的logger实例
        logger1 = get_logger("multi", "instance1")
        logger2 = get_logger("multi", "instance2")
        
        # 创建对应的装饰器
        wrapper1 = create_logger_wrapper(logger1)
        wrapper2 = create_logger_wrapper(logger2)
        
        # 定义使用不同logger的函数
        @wrapper1(level='INFO')
        def func_with_logger1(value):
            """使用logger1的函数"""
            return value * 2
        
        @wrapper2(level='DEBUG')
        def func_with_logger2(value):
            """使用logger2的函数"""
            return value * 3
        
        print("\n1. 使用logger1实例:")
        result1 = func_with_logger1(5)
        print(f"   结果: {result1}")
        
        print("\n2. 使用logger2实例:")
        result2 = func_with_logger2(5)
        print(f"   结果: {result2}")
        
        print("\n✅ 多实例独立性测试完成")
        
    finally:
        # 清理临时配置文件
        if os.path.exists(config_path):
            os.unlink(config_path)

if __name__ == "__main__":
    print("开始测试create_logger_wrapper功能...")
    
    # 运行所有测试
    test_create_logger_wrapper()
    test_comparison_with_logger_wrapper()
    test_multiple_logger_instances()
    
    print("\n🎉 所有测试完成！")
    print("\n请检查生成的日志文件 'test_create_logger_wrapper.log' 以验证日志记录是否正确。")