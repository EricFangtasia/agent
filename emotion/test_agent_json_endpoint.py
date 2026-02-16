#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 .well-known/agent.json 端点
"""
import requests
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_agent_json_endpoint():
    """
    测试 .well-known/agent.json 端点
    """
    try:
        url = "http://localhost:8090/.well-known/agent.json"
        response = requests.get(url)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("\n✓ 端点测试成功!")
        else:
            print(f"\n✗ 端点返回错误状态码: {response.status_code}")
            print(f"错误内容: {response.text}")
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")

if __name__ == "__main__":
    test_agent_json_endpoint()