#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单验证create_logger_wrapper函数的功能
"""

import sys
import os

# 添加src路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tk_base_utils.tk_logger.decorators import create_logger_wrapper, logger_wrapper
from tk_base_utils.tk_logger.logger import get_logger

def main():
    print("=== 验证create_logger_wrapper功能 ===")
    
    # 创建自定义logger实例
    custom_logger = get_logger("multi", "demo_instance")
    
    # 使用create_logger_wrapper创建装饰器
    my_wrapper = create_logger_wrapper(custom_logger)
    
    # 定义测试函数
    @my_wrapper()
    def add_numbers(a, b):
        """加法函数"""
        return a + b
    
    @my_wrapper(level='DEBUG', model='simple')
    def multiply_numbers(x, y):
        """乘法函数"""
        return x * y
    
    # 对比：使用原始logger_wrapper
    @logger_wrapper()
    def subtract_numbers(a, b):
        """减法函数"""
        return a - b
    
    print("\n1. 使用create_logger_wrapper创建的装饰器:")
    result1 = add_numbers(10, 5)
    print(f"   10 + 5 = {result1}")
    
    print("\n2. 使用create_logger_wrapper (simple模式):")
    result2 = multiply_numbers(3, 4)
    print(f"   3 * 4 = {result2}")
    
    print("\n3. 使用原始logger_wrapper对比:")
    result3 = subtract_numbers(10, 3)
    print(f"   10 - 3 = {result3}")
    
    print("\n✅ create_logger_wrapper功能验证完成！")
    print("\n从日志输出可以看到：")
    print("- create_logger_wrapper创建的装饰器使用指定的logger实例")
    print("- 功能与logger_wrapper完全一致")
    print("- 支持所有相同的参数（level, model）")

if __name__ == "__main__":
    main()