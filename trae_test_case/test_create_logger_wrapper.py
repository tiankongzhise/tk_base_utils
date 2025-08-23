#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的调用栈验证测试
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tk_base_utils.tk_logger import get_logger,create_logger_wrapper,set_logger_config_path
from tk_base_utils import find_file
logger_config_path = find_file("logger_test_config.toml")
set_logger_config_path(logger_config_path)
logger = get_logger(mode="multi",instance_name='test_create_logger_wrapper')
logger_wrapper = create_logger_wrapper(logger)

# 使用logger_wrapper装饰器
@logger_wrapper(level='INFO')
def simple_test_function():
    """简单的测试函数"""
    return "success"

if __name__ == "__main__":
    print("调用被装饰的函数...")
    # 这一行调用应该被正确记录为调用位置（第22行）
    result = simple_test_function()
    print(f"函数返回: {result}")
    print("\n检查控制台输出，应该显示 test_simple_callstack_verification.py:22 而不是 decorators.py")
