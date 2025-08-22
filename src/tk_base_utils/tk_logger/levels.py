#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志等级统一管理模块

该模块集中管理所有自定义日志等级的名称和数值映射，
为tk_logger和tk_http等模块提供统一的日志等级定义。
"""

import logging
from typing import Dict, Optional


# 自定义日志等级映射表
# 数值范围说明：
# - 标准等级：DEBUG(10), INFO(20), WARNING(30), ERROR(40), CRITICAL(50)
# - 自定义等级：11-17 (介于DEBUG和INFO之间的细分等级)
CUSTOM_LOG_LEVELS: Dict[str, int] = {
    'INFO_CONFIG': 11,      # 配置相关信息
    'INFO_UTILS': 12,       # 工具类相关信息
    'INFO_DATABASE': 13,    # 数据库相关信息
    'INFO_KERNEL': 14,      # 内核相关信息
    'INFO_CORE': 15,        # 核心功能相关信息
    'INFO_SERVICE': 16,     # 服务相关信息
    'INFO_CONTROL': 17,     # 控制相关信息
}

# 等级名称到数值的完整映射（包含标准等级和自定义等级）
ALL_LOG_LEVELS: Dict[str, int] = {
    # 标准等级
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
    # 自定义等级
    **CUSTOM_LOG_LEVELS
}

# 数值到等级名称的反向映射
LEVEL_NAMES: Dict[int, str] = {v: k for k, v in ALL_LOG_LEVELS.items()}


def get_log_level(level_name: str, default_level: int = logging.INFO) -> int:
    """
    根据等级名称获取对应的数值
    
    Args:
        level_name: 日志等级名称（不区分大小写）
        default_level: 当等级名称无效时返回的默认等级
        
    Returns:
        int: 日志等级数值
        
    Examples:
        >>> get_log_level('DEBUG')
        10
        >>> get_log_level('INFO_UTILS')
        12
        >>> get_log_level('INVALID', logging.WARNING)
        30
    """
    level_name_upper = level_name.upper()
    
    # 首先尝试获取标准日志等级
    standard_level = getattr(logging, level_name_upper, None)
    if standard_level is not None:
        return standard_level
    
    # 然后尝试获取自定义等级
    return ALL_LOG_LEVELS.get(level_name_upper, default_level)


def get_level_name(level_value: int) -> Optional[str]:
    """
    根据等级数值获取对应的名称
    
    Args:
        level_value: 日志等级数值
        
    Returns:
        Optional[str]: 等级名称，如果数值无效则返回None
        
    Examples:
        >>> get_level_name(10)
        'DEBUG'
        >>> get_level_name(12)
        'INFO_UTILS'
        >>> get_level_name(999)
        None
    """
    return LEVEL_NAMES.get(level_value)


def register_custom_levels() -> None:
    """
    向logging模块注册所有自定义日志等级
    
    该函数应在使用自定义等级之前调用，通常在模块初始化时调用。
    重复调用是安全的。
    """
    for level_name, level_value in CUSTOM_LOG_LEVELS.items():
        logging.addLevelName(level_value, level_name)


def is_custom_level(level_name: str) -> bool:
    """
    检查给定的等级名称是否为自定义等级
    
    Args:
        level_name: 日志等级名称（不区分大小写）
        
    Returns:
        bool: 如果是自定义等级返回True，否则返回False
        
    Examples:
        >>> is_custom_level('INFO_UTILS')
        True
        >>> is_custom_level('DEBUG')
        False
    """
    return level_name.upper() in CUSTOM_LOG_LEVELS


def get_custom_levels() -> Dict[str, int]:
    """
    获取所有自定义日志等级的副本
    
    Returns:
        Dict[str, int]: 自定义等级名称到数值的映射
    """
    return CUSTOM_LOG_LEVELS.copy()


def get_all_levels() -> Dict[str, int]:
    """
    获取所有日志等级（标准+自定义）的副本
    
    Returns:
        Dict[str, int]: 所有等级名称到数值的映射
    """
    return ALL_LOG_LEVELS.copy()


# 模块初始化时自动注册自定义等级
register_custom_levels()