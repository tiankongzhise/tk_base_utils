# 装饰器调用栈Bug修复文档

## 问题描述

在使用 `logger_wrapper` 装饰器时，存在一个调用栈获取错误的bug：

- **问题现象**: 日志中记录的文件路径和行号指向 `decorators.py` 而不是实际调用被装饰函数的位置
- **根本原因**: `logger_wrapper` 通过延迟调用 `logger_wrapper_multi` 创建了额外的调用层级，导致调用栈深度计算错误

## 调用栈分析

### 问题调用栈
```
被装饰函数调用位置 (应该记录这里)
  ↓
logger_wrapper.wrapper
  ↓  
logger_wrapper_multi(logger, level, model)(func)
  ↓
logger_wrapper_multi.wrapper (记录了这里 - 错误!)
```

### 修复后调用栈
```
被装饰函数调用位置 (正确记录这里)
  ↓
logger_wrapper.wrapper (检测到并跳过)
  ↓  
logger_wrapper_multi(logger, level, model)(func)
  ↓
logger_wrapper_multi.wrapper (智能向上查找)
```

## 修复方案

在 `logger_wrapper_multi` 函数中添加了智能调用栈检测逻辑：

```python
# 获取调用栈，找到调用被装饰函数的位置
caller_frame = frame.f_back  # wrapper的调用者

# 检查是否通过logger_wrapper间接调用
# 如果caller_frame指向decorators.py中的logger_wrapper，需要再向上一层
if (caller_frame and 
    caller_frame.f_code.co_filename.endswith('decorators.py') and 
    caller_frame.f_code.co_name == 'wrapper'):
    # 这是通过logger_wrapper间接调用的情况，需要再向上一层
    caller_frame = caller_frame.f_back
```

## 修复效果

### 修复前
```
2025-08-23 17:10:55 - logger - INFO - [decorators.py:54] - 函数调用开始...
```

### 修复后  
```
2025-08-23 17:10:55 - logger - INFO - [test_file.py:22] - 函数调用开始...
```

## 测试验证

创建了以下测试文件验证修复效果：

1. **test_decorator_callstack_fix.py**: 全面测试不同装饰器场景
   - `logger_wrapper` 装饰器测试
   - `logger_wrapper_multi` 装饰器测试  
   - 嵌套调用测试

2. **test_simple_callstack_verification.py**: 简单验证测试

### 测试结果

✅ **logger_wrapper**: 正确记录调用位置 `test_decorator_callstack_fix.py:77`
✅ **logger_wrapper_multi**: 正确记录调用位置 `test_decorator_callstack_fix.py:90`  
✅ **嵌套调用**: 正确记录调用位置 `test_decorator_callstack_fix.py:129`

## 影响范围

- **修复文件**: `src/tk_base_utils/tk_logger/decorators.py`
- **影响功能**: `logger_wrapper` 和 `logger_wrapper_multi` 装饰器的调用位置记录
- **向后兼容**: 完全兼容，不影响现有API
- **性能影响**: 微小的额外检查开销，可忽略不计

## 总结

这个修复解决了装饰器调用栈获取错误的关键bug，确保日志能够准确记录被装饰函数的实际调用位置，大大提升了日志的调试价值和可读性。修复方案通过智能检测调用栈中的装饰器层级，自动调整到正确的调用位置，既解决了问题又保持了代码的简洁性。