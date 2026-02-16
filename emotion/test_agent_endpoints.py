#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试新增的agentCard端点
"""
import requests
import sys
import os
import json

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_agent_card_endpoint():
    """测试agentCard端点"""
    print("测试 /agentCard 端点...")
    try:
        url = "http://localhost:8090/agentCard"
        response = requests.get(url, timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("成功获取 agentCard 配置!")
            print("配置预览:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求 agentCard 端点时出现异常: {e}")

def test_well_known_endpoint():
    """测试.well-known/agent.json端点"""
    print("\n测试 /.well-known/agent.json 端点...")
    try:
        url = "http://localhost:8090/.well-known/agent.json"
        response = requests.get(url, timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("成功获取 agent.json 配置!")
            print("配置预览:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求 .well-known/agent.json 端点时出现异常: {e}")

def test_health_endpoint():
    """测试健康检查端点"""
    print("\n测试 /health 端点...")
    try:
        url = "http://localhost:8090/health"
        response = requests.get(url, timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"健康状态: {data}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求 health 端点时出现异常: {e}")

if __name__ == "__main__":
    print("开始测试新增的端点...")
    test_agent_card_endpoint()
    test_well_known_endpoint()
    test_health_endpoint()
    print("\n端点测试完成")