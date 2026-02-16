#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
情绪分析意图适配器测试脚本
"""
import requests
import json
import logging
import base64

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 服务地址
INTENT_ADAPTER_URL = "http://localhost:8090"
MCP_SERVICE_URL = "http://localhost:8089"


def test_agentcard_endpoint():
    """
    测试获取AgentCard
    """
    logger.info("测试 /agentcard 端点...")
    try:
        response = requests.get(f"{INTENT_ADAPTER_URL}/agentcard")
        if response.status_code == 200:
            agentcard = response.json()
            logger.info("AgentCard获取成功")
            print(json.dumps(agentcard, indent=2, ensure_ascii=False))
            return True
        else:
            logger.error(f"获取AgentCard失败: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"请求AgentCard时出错: {e}")
        return False


def test_health_check():
    """
    测试健康检查
    """
    logger.info("测试 /health 端点...")
    try:
        response = requests.get(f"{INTENT_ADAPTER_URL}/health")
        if response.status_code == 200:
            health_status = response.json()
            logger.info(f"健康检查结果: {health_status}")
            return True
        else:
            logger.error(f"健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"健康检查请求时出错: {e}")
        return False


def test_process_intent():
    """
    测试意图处理
    """
    logger.info("测试 /process-intent 端点...")
    
    # 创建一个模拟请求
    test_request = {
        "message": {
            "parts": [
                {
                    "kind": "text",
                    "text": "分析这张图片中人物的情绪"
                }
            ],
            "metadata": {
                "intentInfos": [
                    {
                        "intent": "emotion-analysis",
                        "slots": [
                            {
                                "name": "image_base64",
                                "value": ""  # 空的base64字符串，用于测试错误处理
                            }
                        ]
                    }
                ]
            }
        }
    }
    
    try:
        response = requests.post(
            f"{INTENT_ADAPTER_URL}/process-intent",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info("意图处理请求成功")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return True
        else:
            logger.error(f"意图处理失败: {response.status_code}")
            logger.error(f"响应内容: {response.text}")
            return False
    except Exception as e:
        logger.error(f"意图处理请求时出错: {e}")
        return False


def test_mcp_service():
    """
    测试MCP服务是否正常
    """
    logger.info("测试MCP服务 /execute 端点...")
    
    test_payload = {
        "image_base64": ""  # 空的base64字符串，用于测试错误处理
    }
    
    try:
        response = requests.post(
            f"{MCP_SERVICE_URL}/execute",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info("MCP服务请求成功")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return True
        else:
            logger.error(f"MCP服务请求失败: {response.status_code}")
            logger.error(f"响应内容: {response.text}")
            return False
    except Exception as e:
        logger.error(f"MCP服务请求时出错: {e}")
        return False


def main():
    """
    主函数，测试所有功能
    """
    logger.info("开始测试情绪分析意图适配器...")
    
    print("\n1. 测试AgentCard获取:")
    test_agentcard_endpoint()
    
    print("\n2. 测试健康检查:")
    test_health_check()
    
    print("\n3. 测试MCP服务:")
    test_mcp_service()
    
    print("\n4. 测试意图处理:")
    test_process_intent()
    
    logger.info("\n测试完成")


if __name__ == "__main__":
    main()