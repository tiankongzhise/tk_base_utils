#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的调用栈验证测试
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tk_base_utils.tk_logger.decorators import logger_wrapper

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
