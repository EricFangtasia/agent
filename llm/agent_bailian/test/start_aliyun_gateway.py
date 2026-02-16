#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动阿里云实时多模态交互网关

使用此脚本启动网关服务，它将作为本地客户端和阿里云服务之间的桥梁
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def check_api_key():
    """检查是否设置了API密钥"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误: DASHSCOPE_API_KEY 环境变量未设置")
        print("\n请设置您的阿里云API密钥:")
        print("Linux/macOS:")
        print("  export DASHSCOPE_API_KEY='your-api-key-here'")
        print("\nWindows (CMD):")
        print("  set DASHSCOPE_API_KEY=your-api-key-here")
        print("\nWindows (PowerShell):")
        print("  $env:DASHSCOPE_API_KEY=\"your-api-key-here\"")
        print("\n或者您可以直接在代码中设置API_KEY变量")
        return False
    return True


def main():
    """主函数，启动网关服务"""
    print("🚀 启动阿里云实时多模态交互网关")
    print("-" * 50)
    
    # 检查API密钥
    if not check_api_key():
        return
    
    # 检查是否可以导入websockets
    try:
        import websockets
        print("✅ websockets 库已安装")
    except ImportError:
        print("❌ websockets 库未安装")
        print("请运行: pip install websockets")
        return
    
    # 导入网关类
    try:
        from aliyun_realtime_multimodal_gateway import main as gateway_main
        print("✅ 网关模块已找到")
    except ImportError as e:
        print(f"❌ 无法导入网关模块: {e}")
        return
    
    print(f"🌐 网关将监听 localhost:8765")
    print(f"☁️  阿里云服务地址: wss://dashscope.aliyuncs.com/api-ws/v1/inference")
    print("\n按 Ctrl+C 停止服务\n")
    
    try:
        # 启动网关
        gateway_main()
    except KeyboardInterrupt:
        print("\n\n🛑 网关服务已停止")
    except Exception as e:
        print(f"\n❌ 启动网关时出错: {e}")
        import traceback
        traceback.print_exc()


def run_test():
    """运行测试"""
    print("🧪 运行网关测试")
    print("-" * 50)
    
    # 检查API密钥
    if not check_api_key():
        return
    
    try:
        from test_aliyun_gateway import run_test as run_gateway_test
        print("✅ 测试模块已找到")
        
        print("运行测试...")
        run_gateway_test()
    except ImportError as e:
        print(f"❌ 无法导入测试模块: {e}")


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            run_test()
        else:
            print("用法: python start_aliyun_gateway.py [test]")
            print("  不带参数: 启动网关服务")
            print("  test:     运行测试")
    else:
        main()