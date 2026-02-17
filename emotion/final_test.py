#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终测试脚本
"""
import requests
import sys
import os
import json

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    # 测试 .well-known/agent.json 端点
    print("测试 .well-known/agent.json 端点...")
    url = "http://localhost:8090/.well-known/agent.json"
    response = requests.get(url, timeout=10)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("成功获取 agent.json 配置!")
        data = response.json()
        print("配置预览:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")
    else:
        print(f"请求失败: {response.text}")
        
    # 测试健康检查
    print("\n测试健康检查端点...")
    health_url = "http://localhost:8090/health"
    health_resp = requests.get(health_url, timeout=10)
    print(f"健康检查状态: {health_resp.status_code}")
    
except Exception as e:
    print(f"测试过程中出现异常: {e}")
    import traceback
    traceback.print_exc()