#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证测试 - 验证logger优化后的所有功能
"""

import sys
from pathlib import Path

# 添加项目路径到sys.path
project_root = Path(__file__).parent / "src"
sys.path.insert(0, str(project_root))

def test_singleton_logger():
    """测试单例logger"""
    print("=== 测试单例logger ===")
    
    from tk_base_utils.tk_logger import get_logger
    
    logger1 = get_logger()
    logger2 = get_logger()
    
    if logger1 is logger2:
        print("✅ 单例logger工作正常")
        return True
    else:
        print("❌ 单例logger失败")
        return False

def test_multi_instance_logger():
    """测试多实例logger"""
    print("\n=== 测试多实例logger ===")
    
    from tk_base_utils.tk_logger import MultiInstanceLogger
    
    multi_logger = MultiInstanceLogger()
    
    logger1 = multi_logger.get_logger("test1")
    logger2 = multi_logger.get_logger("test2")
    logger3 = multi_logger.get_logger("test1")  # 应该返回相同实例
    
    if logger1 is not logger2 and logger1 is logger3:
        print("✅ 多实例logger工作正常")
        return True
    else:
        print("❌ 多实例logger失败")
        return False

def test_logger_wrapper():
    """测试logger_wrapper装饰器"""
    print("\n=== 测试logger_wrapper装饰器 ===")
    
    from tk_base_utils.tk_logger import logger_wrapper
    from tk_base_utils.tk_logger.logger import SingletonLogger
    
    # 重置logger状态
    SingletonLogger.reset()
    
    @logger_wrapper(level="INFO")
    def test_function(x, y):
        return x + y
    
    # 调用函数
    result = test_function(5, 3)
    
    if result == 8 and SingletonLogger._instance is not None:
        print("✅ logger_wrapper装饰器工作正常")
        return True
    else:
        print("❌ logger_wrapper装饰器失败")
        return False

def test_logger_wrapper_multi():
    """测试logger_wrapper_multi装饰器"""
    print("\n=== 测试logger_wrapper_multi装饰器 ===")
    
    from tk_base_utils.tk_logger import logger_wrapper_multi, MultiInstanceLogger
    
    multi_logger = MultiInstanceLogger()
    logger_instance = multi_logger.get_logger("test_wrapper")
    
    @logger_wrapper_multi(logger_instance, level="INFO")
    def test_function_multi(a, b):
        return a * b
    
    # 调用函数
    result = test_function_multi(4, 6)
    
    if result == 24:
        print("✅ logger_wrapper_multi装饰器工作正常")
        return True
    else:
        print("❌ logger_wrapper_multi装饰器失败")
        return False

def test_base_logger_inheritance():
    """测试BaseLogger继承"""
    print("\n=== 测试BaseLogger继承 ===")
    
    from tk_base_utils.tk_logger.logger import SingletonLogger, MultiInstanceLogger, BaseLogger
    
    if issubclass(SingletonLogger, BaseLogger) and issubclass(MultiInstanceLogger, BaseLogger):
        print("✅ BaseLogger继承正常")
        return True
    else:
        print("❌ BaseLogger继承失败")
        return False

def test_import_behavior():
    """测试导入行为"""
    print("\n=== 测试导入行为 ===")
    
    from tk_base_utils.tk_logger.logger import SingletonLogger
    
    # 重置logger状态
    SingletonLogger.reset()
    
    # 重新导入装饰器
    if 'tk_base_utils.tk_logger.decorators' in sys.modules:
        del sys.modules['tk_base_utils.tk_logger.decorators']
    
    from tk_base_utils.tk_logger.decorators import logger_wrapper
    
    if SingletonLogger._instance is None:
        print("✅ 导入时没有提前初始化logger")
        return True
    else:
        print("❌ 导入时提前初始化了logger")
        return False

def main():
    """运行所有测试"""
    print("开始最终验证测试...")
    
    tests = [
        test_singleton_logger,
        test_multi_instance_logger,
        test_logger_wrapper,
        test_logger_wrapper_multi,
        test_base_logger_inheritance,
        test_import_behavior
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_func.__name__} 失败")
        except Exception as e:
            print(f"❌ {test_func.__name__} 异常: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n=== 最终测试总结 ===")
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有功能验证通过！logger优化和bug修复成功！")
        return True
    else:
        print("⚠️  部分功能验证失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)