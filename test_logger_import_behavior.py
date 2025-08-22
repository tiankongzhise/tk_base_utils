#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试logger_wrapper的导入行为
验证修复后的logger_wrapper不会在导入时提前初始化logger实例
"""

import sys
from pathlib import Path

# 添加项目路径到sys.path
project_root = Path(__file__).parent / "src"
sys.path.insert(0, str(project_root))

def test_import_behavior():
    """测试导入时的行为"""
    print("=== 测试logger_wrapper导入行为 ===")
    
    # 在导入前检查SingletonLogger的状态
    from tk_base_utils.tk_logger.logger import SingletonLogger
    
    print(f"导入前 - SingletonLogger._instance: {SingletonLogger._instance}")
    print(f"导入前 - SingletonLogger._initialized: {SingletonLogger._initialized}")
    
    # 导入logger_wrapper装饰器
    print("\n正在导入logger_wrapper...")
    from tk_base_utils.tk_logger import logger_wrapper
    
    # 检查导入后的状态
    print(f"导入后 - SingletonLogger._instance: {SingletonLogger._instance}")
    print(f"导入后 - SingletonLogger._initialized: {SingletonLogger._initialized}")
    
    if SingletonLogger._instance is None and not SingletonLogger._initialized:
        print("✅ 导入logger_wrapper时没有提前初始化logger实例")
        return True
    else:
        print("❌ 导入logger_wrapper时提前初始化了logger实例")
        return False

def test_decorator_usage():
    """测试装饰器的实际使用"""
    print("\n=== 测试装饰器实际使用 ===")
    
    from tk_base_utils.tk_logger import logger_wrapper
    from tk_base_utils.tk_logger.logger import SingletonLogger
    
    # 重置logger状态
    SingletonLogger.reset()
    
    print(f"装饰器定义前 - SingletonLogger._instance: {SingletonLogger._instance}")
    
    # 定义带装饰器的函数
    @logger_wrapper(level="INFO", model="simple")
    def test_function(x, y):
        """测试函数"""
        return x + y
    
    print(f"装饰器定义后 - SingletonLogger._instance: {SingletonLogger._instance}")
    
    if SingletonLogger._instance is None:
        print("✅ 定义装饰器函数时没有初始化logger实例")
    else:
        print("❌ 定义装饰器函数时提前初始化了logger实例")
        return False
    
    # 调用函数
    print("\n调用装饰器函数...")
    result = test_function(3, 4)
    
    print(f"函数调用后 - SingletonLogger._instance: {SingletonLogger._instance}")
    print(f"函数调用后 - SingletonLogger._initialized: {SingletonLogger._initialized}")
    print(f"函数返回值: {result}")
    
    if SingletonLogger._instance is not None and SingletonLogger._initialized:
        print("✅ 调用装饰器函数时正确初始化了logger实例")
        return True
    else:
        print("❌ 调用装饰器函数时没有正确初始化logger实例")
        return False

def test_multiple_imports():
    """测试多次导入的行为"""
    print("\n=== 测试多次导入行为 ===")
    
    from tk_base_utils.tk_logger.logger import SingletonLogger
    
    # 重置logger状态
    SingletonLogger.reset()
    
    print(f"重置后 - SingletonLogger._instance: {SingletonLogger._instance}")
    
    # 多次导入
    for i in range(3):
        print(f"\n第{i+1}次导入logger_wrapper...")
        
        # 删除模块缓存，强制重新导入
        if 'tk_base_utils.tk_logger.decorators' in sys.modules:
            del sys.modules['tk_base_utils.tk_logger.decorators']
        
        from tk_base_utils.tk_logger.decorators import logger_wrapper
        
        print(f"第{i+1}次导入后 - SingletonLogger._instance: {SingletonLogger._instance}")
        
        if SingletonLogger._instance is not None:
            print(f"❌ 第{i+1}次导入时提前初始化了logger实例")
            return False
    
    print("✅ 多次导入都没有提前初始化logger实例")
    return True

def test_concurrent_decorators():
    """测试并发装饰器定义"""
    print("\n=== 测试并发装饰器定义 ===")
    
    from tk_base_utils.tk_logger import logger_wrapper
    from tk_base_utils.tk_logger.logger import SingletonLogger
    
    # 重置logger状态
    SingletonLogger.reset()
    
    # 定义多个装饰器函数
    @logger_wrapper(level="INFO")
    def func1():
        return "func1"
    
    @logger_wrapper(level="DEBUG")
    def func2():
        return "func2"
    
    @logger_wrapper(level="WARNING", model="simple")
    def func3():
        return "func3"
    
    print(f"定义多个装饰器函数后 - SingletonLogger._instance: {SingletonLogger._instance}")
    
    if SingletonLogger._instance is None:
        print("✅ 定义多个装饰器函数时没有提前初始化logger实例")
    else:
        print("❌ 定义多个装饰器函数时提前初始化了logger实例")
        return False
    
    # 调用第一个函数
    print("\n调用第一个装饰器函数...")
    result1 = func1()
    
    if SingletonLogger._instance is not None:
        print("✅ 调用第一个函数后正确初始化了logger实例")
        
        # 调用其他函数，应该使用同一个logger实例
        logger_instance = SingletonLogger._instance
        
        result2 = func2()
        result3 = func3()
        
        if SingletonLogger._instance is logger_instance:
            print("✅ 所有装饰器函数使用同一个logger实例")
            return True
        else:
            print("❌ 装饰器函数使用了不同的logger实例")
            return False
    else:
        print("❌ 调用函数后没有正确初始化logger实例")
        return False

def main():
    """运行所有测试"""
    print("开始测试logger_wrapper的导入行为...")
    
    tests = [
        test_import_behavior,
        test_decorator_usage,
        test_multiple_imports,
        test_concurrent_decorators
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_func.__name__} 通过")
            else:
                print(f"❌ {test_func.__name__} 失败")
        except Exception as e:
            print(f"❌ {test_func.__name__} 异常: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n=== 测试总结 ===")
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！logger_wrapper导入行为修复成功！")
        return True
    else:
        print("⚠️  部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)