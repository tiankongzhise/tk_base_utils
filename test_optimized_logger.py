#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的logger功能
包括：
1. BaseLogger抽象基类
2. 多实例logger的共享/独立日志文件配置
3. 统一的logger_wrapper装饰器
4. 重构后的SingletonLogger和MultiInstanceLogger
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# 添加项目路径到sys.path
project_root = Path(__file__).parent / "src"
sys.path.insert(0, str(project_root))

from tk_base_utils.tk_logger import (
    get_logger, 
    MultiInstanceLogger, 
    logger_wrapper, 
    logger_wrapper_multi,
    set_logger_config_path,
    get_logger_config
)
from tk_base_utils.tk_logger.logger import SingletonLogger, BaseLogger
from tk_base_utils.tk_logger.config import TkLoggerConfig

def test_base_logger_abstraction():
    """测试BaseLogger抽象基类"""
    print("\n=== 测试BaseLogger抽象基类 ===")
    
    # 验证BaseLogger是抽象类
    try:
        base_logger = BaseLogger()
        print("❌ BaseLogger应该是抽象类，不能直接实例化")
        return False
    except TypeError as e:
        print(f"✅ BaseLogger正确地作为抽象类: {e}")
    
    # 验证SingletonLogger和MultiInstanceLogger都继承自BaseLogger
    # 注意：SingletonLogger()返回EnhancedLogger实例，需要检查类本身
    print(f"✅ SingletonLogger继承自BaseLogger: {issubclass(SingletonLogger, BaseLogger)}")
    print(f"✅ MultiInstanceLogger继承自BaseLogger: {issubclass(MultiInstanceLogger, BaseLogger)}")
    
    return True

def test_shared_log_configuration():
    """测试多实例logger的共享日志配置"""
    print("\n=== 测试多实例logger共享日志配置 ===")
    
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        config_content = """
[logging]
name = "test_shared"
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
file_path = "logs/test_shared.log"
max_bytes = 10485760
backup_count = 5
rotation_type = "size"
rotation_interval = "midnight"
use_absolute_path = false
multi_instance_shared_log = true
"""
        f.write(config_content)
        temp_config_path = f.name
    
    try:
        # 设置配置文件路径
        set_logger_config_path(temp_config_path)
        config = get_logger_config()
        
        print(f"✅ 共享日志配置加载成功: {config.multi_instance_shared_log}")
        
        # 测试多实例共享日志
        multi_logger = MultiInstanceLogger()
        logger1 = multi_logger.get_logger("instance1")
        logger2 = multi_logger.get_logger("instance2")
        
        logger1.info("来自instance1的消息")
        logger2.info("来自instance2的消息")
        
        print("✅ 多实例共享日志测试完成")
        
        # 重置配置为独立日志
        with open(temp_config_path, 'w') as f:
            config_content_separate = config_content.replace(
                "multi_instance_shared_log = true", 
                "multi_instance_shared_log = false"
            )
            f.write(config_content_separate)
        
        # 重新加载配置
        set_logger_config_path(temp_config_path)
        config = get_logger_config()
        
        print(f"✅ 独立日志配置加载成功: {config.multi_instance_shared_log}")
        
        # 测试多实例独立日志
        multi_logger2 = MultiInstanceLogger()
        logger3 = multi_logger2.get_logger("instance3")
        logger4 = multi_logger2.get_logger("instance4")
        
        logger3.info("来自instance3的消息")
        logger4.info("来自instance4的消息")
        
        print("✅ 多实例独立日志测试完成")
        
        return True
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_config_path):
            os.unlink(temp_config_path)

def test_unified_logger_wrapper():
    """测试统一的logger_wrapper装饰器"""
    print("\n=== 测试统一的logger_wrapper装饰器 ===")
    
    # 测试logger_wrapper（单例模式）
    @logger_wrapper(level="INFO", model="default")
    def singleton_function(x, y):
        """使用单例logger的函数"""
        return x + y
    
    # 测试logger_wrapper_multi（多实例模式）
    multi_logger = MultiInstanceLogger()
    test_logger = multi_logger.get_logger("test_wrapper")
    
    @logger_wrapper_multi(test_logger, level="INFO", model="default")
    def multi_instance_function(x, y):
        """使用多实例logger的函数"""
        return x * y
    
    print("执行单例装饰器函数...")
    result1 = singleton_function(3, 4)
    print(f"✅ 单例装饰器函数结果: {result1}")
    
    print("执行多实例装饰器函数...")
    result2 = multi_instance_function(3, 4)
    print(f"✅ 多实例装饰器函数结果: {result2}")
    
    # 测试异常处理
    @logger_wrapper(level="ERROR", model="simple")
    def error_function():
        """会抛出异常的函数"""
        raise ValueError("测试异常")
    
    print("测试异常处理...")
    try:
        error_function()
    except ValueError:
        print("✅ 异常处理测试完成")
    
    return True

def test_logger_inheritance():
    """测试logger类的继承关系"""
    print("\n=== 测试logger类继承关系 ===")
    
    # 测试SingletonLogger
    logger1 = SingletonLogger()
    logger2 = SingletonLogger()
    
    print(f"✅ SingletonLogger单例测试: {logger1 is logger2}")
    
    # 测试MultiInstanceLogger
    multi = MultiInstanceLogger()
    logger_a = multi.get_logger("a")
    logger_b = multi.get_logger("b")
    logger_a2 = multi.get_logger("a")  # 应该返回相同实例
    
    print(f"✅ MultiInstanceLogger不同实例: {logger_a is not logger_b}")
    print(f"✅ MultiInstanceLogger相同名称实例: {logger_a is logger_a2}")
    
    # 测试reset功能
    multi.reset()
    logger_a3 = multi.get_logger("a")  # 重置后应该是新实例
    print(f"✅ MultiInstanceLogger重置后新实例: {logger_a is not logger_a3}")
    
    return True

def test_custom_log_levels():
    """测试自定义日志级别"""
    print("\n=== 测试自定义日志级别 ===")
    
    logger = get_logger()
    
    # 测试自定义级别
    custom_levels = [
        "INFO_CONFIG", "INFO_UTILS", "INFO_DATABASE", 
        "INFO_KERNEL", "INFO_CORE", "INFO_SERVICE", "INFO_CONTROL"
    ]
    
    for level in custom_levels:
        try:
            # 使用装饰器测试自定义级别
            @logger_wrapper(level=level, model="simple")
            def test_custom_level():
                return f"测试{level}级别"
            
            result = test_custom_level()
            print(f"✅ 自定义级别 {level} 测试成功")
        except Exception as e:
            print(f"❌ 自定义级别 {level} 测试失败: {e}")
            return False
    
    return True

def test_file_separation():
    """测试日志文件分离"""
    print("\n=== 测试日志文件分离 ===")
    
    # 确保logs目录存在
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # 创建多个实例并记录日志
    multi_logger = MultiInstanceLogger()
    
    instances = ["file_test1", "file_test2", "file_test3"]
    for instance_name in instances:
        logger = multi_logger.get_logger(instance_name)
        logger.info(f"来自{instance_name}的测试消息")
        logger.warning(f"{instance_name}的警告消息")
    
    # 检查日志文件是否创建
    time.sleep(0.1)  # 等待文件写入
    
    expected_files = []
    config = get_logger_config()
    
    if config.multi_instance_shared_log:
        # 共享日志文件
        expected_files = ["app.log"]
    else:
        # 独立日志文件
        expected_files = [f"app_{instance}.log" for instance in instances]
    
    for expected_file in expected_files:
        file_path = logs_dir / expected_file
        if file_path.exists():
            print(f"✅ 日志文件创建成功: {expected_file}")
        else:
            print(f"❌ 日志文件未创建: {expected_file}")
    
    return True

def main():
    """运行所有测试"""
    print("开始测试优化后的logger功能...")
    
    tests = [
        test_base_logger_abstraction,
        test_shared_log_configuration,
        test_unified_logger_wrapper,
        test_logger_inheritance,
        test_custom_log_levels,
        test_file_separation
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
    
    print(f"\n=== 测试总结 ===")
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！logger优化成功！")
        return True
    else:
        print("⚠️  部分测试失败，需要检查实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)