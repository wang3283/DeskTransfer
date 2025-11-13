#!/usr/bin/env python3
"""
版本信息管理
"""

__version__ = "1.0.0"
__author__ = "DeskTransfer Team"
__description__ = "局域网图片传输工具"
__app_name__ = "DeskTransfer"

VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_BUILD = 0

def get_version_string():
    """获取版本字符串"""
    return f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"

def get_version_tuple():
    """获取版本元组"""
    return (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, VERSION_BUILD)

def get_app_info():
    """获取应用信息"""
    return {
        "name": __app_name__,
        "version": get_version_string(),
        "description": __description__,
        "author": __author__,
    }

if __name__ == "__main__":
    print(f"{__app_name__} v{get_version_string()}")
    print(f"描述: {__description__}")
    print(f"作者: {__author__}")
