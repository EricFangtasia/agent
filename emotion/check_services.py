#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查服务是否正在运行
"""
import requests
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_services():
    """
    检查服务状态
    """
    try:
        # 检查MCP服务
        mcp_response = requests.get("http://localhost:8089/health", timeout=5)
        print(f"MCP服务状态: {mcp_response.status_code if mcp_response.status_code else 'Failed'}")
        
        # 检查意图适配器服务
        adapter_response = requests.get("http://localhost:8090/health", timeout=5)
        print(f"Intent适配器状态: {adapter_response.status_code if adapter_response.status_code else 'Failed'}")
        
        if mcp_response.status_code == 200:
            print("✓ MCP服务运行正常")
        else:
            print("✗ MCP服务未运行")
            
        if adapter_response.status_code == 200:
            print("✓ Intent适配器运行正常")
        else:
            print("✗ Intent适配器未运行")
            
    except Exception as e:
        print(f"检查服务时出错: {e}")

if __name__ == "__main__":
    check_services()