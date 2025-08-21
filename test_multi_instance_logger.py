#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多例Logger功能

测试内容：
1. 测试MultiInstanceLogger的基本功能
2. 测试get_logger函数的单例/多例模式切换
3. 测试logger_wrapper_multi装饰器
4. 测试实例管理功能
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目路径到sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from tk_base_utils.tk_logger import (
    get_logger, 
    MultiInstanceLogger, 
    logger_wrapper_multi,
    set_logger_config_path
)

def find_file(filename, search_dir):
    """简单的文件查找函数"""
    search_path = Path(search_dir)
    if search_path.exists():
        for file_path in search_path.rglob(filename):
            return str(file_path)
    return None

def test_singleton_vs_multi():
    """测试单例和多例模式"""
    print("\n=== 测试单例和多例模式 ===")
    
    # 测试单例模式（默认）
    logger1 = get_logger()
    logger2 = get_logger()
    print(f"单例模式 - logger1 == logger2: {logger1 is logger2}")
    
    # 测试多例模式
    multi_logger1 = get_logger("multi", "instance1")
    multi_logger2 = get_logger("multi", "instance2")
    multi_logger3 = get_logger("multi", "instance1")  # 相同实例名
    
    print(f"多例模式 - multi_logger1 == multi_logger2: {multi_logger1 is multi_logger2}")
    print(f"多例模式 - multi_logger1 == multi_logger3: {multi_logger1 is multi_logger3}")
    
    # 测试日志记录
    logger1.info("单例logger的日志")
    multi_logger1.info("多例logger1的日志")
    multi_logger2.info("多例logger2的日志")

def test_instance_management():
    """测试实例管理功能"""
    print("\n=== 测试实例管理功能 ===")
    
    # 清空现有实例
    MultiInstanceLogger.reset()
    
    # 创建多个实例
    logger_a = get_logger("multi", "instance_a")
    logger_b = get_logger("multi", "instance_b")
    logger_c = get_logger("multi", "instance_c")
    
    # 获取所有实例
    instances = MultiInstanceLogger.get_instances()
    print(f"当前实例数量: {len(instances)}")
    print(f"实例名称: {list(instances.keys())}")
    
    # 测试实例属性（需要创建一个实例来访问）
    temp_instance = MultiInstanceLogger()
    # 注意：由于MultiInstanceLogger没有__new__方法，我们需要直接访问类方法
    print(f"通过类方法获取实例: {list(MultiInstanceLogger.get_instances().keys())}")
    
    # 重置单个实例
    MultiInstanceLogger.reset("instance_b")
    instances_after_reset = MultiInstanceLogger.get_instances()
    print(f"重置instance_b后的实例: {list(instances_after_reset.keys())}")
    
    # 重置所有实例
    MultiInstanceLogger.reset()
    instances_after_full_reset = MultiInstanceLogger.get_instances()
    print(f"重置所有实例后的实例数量: {len(instances_after_full_reset)}")

def test_logger_wrapper_multi():
    """测试多例版本的logger_wrapper装饰器"""
    print("\n=== 测试多例版本的logger_wrapper装饰器 ===")
    
    # 创建不同的logger实例
    logger_math = get_logger("multi", "math_operations")
    logger_string = get_logger("multi", "string_operations")
    
    @logger_wrapper_multi(logger_math, level="INFO", model="default")
    def add_numbers(a, b):
        """数学加法操作"""
        return a + b
    
    @logger_wrapper_multi(logger_string, level="DEBUG", model="simple")
    def concat_strings(s1, s2):
        """字符串连接操作"""
        return s1 + s2
    
    @logger_wrapper_multi(logger_math, level="INFO_UTILS")
    def multiply_numbers(x, y):
        """数学乘法操作"""
        return x * y
    
    # 测试装饰器功能
    result1 = add_numbers(10, 20)
    result2 = concat_strings("Hello", " World")
    result3 = multiply_numbers(5, 6)
    
    print(f"add_numbers(10, 20) = {result1}")
    print(f"concat_strings('Hello', ' World') = {result2}")
    print(f"multiply_numbers(5, 6) = {result3}")
    
    # 测试异常情况
    @logger_wrapper_multi(logger_math, level="ERROR")
    def divide_numbers(a, b):
        """数学除法操作（可能出现异常）"""
        return a / b
    
    try:
        result4 = divide_numbers(10, 0)
    except ZeroDivisionError as e:
        print(f"捕获到预期的异常: {e}")

def test_custom_log_levels():
    """测试自定义日志级别"""
    print("\n=== 测试自定义日志级别 ===")
    
    # 创建专门的logger实例
    config_logger = get_logger("multi", "config_test")
    utils_logger = get_logger("multi", "utils_test")
    
    # 测试各种自定义日志级别
    config_logger.info_config("这是CONFIG级别的日志")
    config_logger.info_utils("这是UTILS级别的日志")
    config_logger.info_database("这是DATABASE级别的日志")
    
    utils_logger.info_kernel("这是KERNEL级别的日志")
    utils_logger.info_core("这是CORE级别的日志")
    utils_logger.info_service("这是SERVICE级别的日志")
    utils_logger.info_control("这是CONTROL级别的日志")
    
    # 测试标准日志级别
    config_logger.debug("这是DEBUG级别的日志")
    config_logger.info("这是INFO级别的日志")
    config_logger.warning("这是WARNING级别的日志")
    config_logger.error("这是ERROR级别的日志")

def test_file_separation():
    """测试多例logger的文件分离功能"""
    print("\n=== 测试多例logger的文件分离功能 ===")
    
    # 创建不同的logger实例
    file_logger1 = get_logger("multi", "file_test1")
    file_logger2 = get_logger("multi", "file_test2")
    
    # 记录一些日志
    file_logger1.info("这是file_test1实例的日志")
    file_logger2.info("这是file_test2实例的日志")
    
    print("多例logger应该创建独立的日志文件")
    print("请检查日志目录中是否有对应的文件：")
    print("- app_file_test1.log")
    print("- app_file_test2.log")

def main():
    """主测试函数"""
    print("开始测试多例Logger功能...")
    
    # 设置测试配置
    config_path = find_file("test_log_config.toml", "test")
    if config_path:
        set_logger_config_path(config_path)
        print(f"使用配置文件: {config_path}")
    else:
        print("警告: 未找到test_log_config.toml，使用默认配置")
    
    try:
        # 运行各项测试
        test_singleton_vs_multi()
        test_instance_management()
        test_logger_wrapper_multi()
        test_custom_log_levels()
        test_file_separation()
        
        print("\n=== 所有测试完成 ===")
        print("多例Logger功能测试成功！")
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)