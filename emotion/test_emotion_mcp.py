#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
情绪分析MCP服务测试脚本
"""
import requests
import base64
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_emotion_mcp_service():
    """
    测试情绪分析MCP服务
    """
    # 服务地址
    service_url = "http://localhost:8089"
    
    # 读取测试图片并转换为base64
    test_image_path = input("请输入要分析的图片路径: ").strip()
    
    if not test_image_path or not test_image_path.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        # 如果没有提供有效的图片路径，使用模拟的base64字符串
        logger.info("未提供有效图片，使用模拟数据进行测试...")
        image_base64 = ""
    else:
        try:
            with open(test_image_path, "rb") as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"读取图片文件失败: {e}")
            return

    # 测试manifest端点
    logger.info("测试 /manifest 端点...")
    try:
        manifest_response = requests.get(f"{service_url}/manifest")
        if manifest_response.status_code == 200:
            manifest_data = manifest_response.json()
            logger.info(f"MCP服务清单: {manifest_data}")
        else:
            logger.error(f"获取清单失败: {manifest_response.status_code}")
    except Exception as e:
        logger.error(f"请求清单时出错: {e}")

    # 测试健康检查端点
    logger.info("测试 /health 端点...")
    try:
        health_response = requests.get(f"{service_url}/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            logger.info(f"健康检查结果: {health_data}")
        else:
            logger.error(f"健康检查失败: {health_response.status_code}")
    except Exception as e:
        logger.error(f"健康检查请求时出错: {e}")

    # 测试execute端点（如果提供了图片）
    if image_base64:
        logger.info("测试 /execute 端点...")
        try:
            payload = {
                "image_base64": image_base64
            }
            
            execute_response = requests.post(
                f"{service_url}/execute",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if execute_response.status_code == 200:
                result = execute_response.json()
                logger.info(f"情绪分析结果: {result}")
            else:
                logger.error(f"执行分析失败: {execute_response.status_code}, {execute_response.text}")
        except Exception as e:
            logger.error(f"执行分析请求时出错: {e}")
    else:
        logger.info("跳过执行测试（未提供图片）")


def test_with_sample_payload():
    """
    使用示例负载测试服务
    """
    service_url = "http://localhost:8089"
    
    # 示例payload（没有图片数据）
    sample_payload = {
        "image_base64": ""  # 空的base64字符串，用于测试错误处理
    }
    
    logger.info("使用示例负载测试 /execute 端点...")
    try:
        response = requests.post(
            f"{service_url}/execute",
            json=sample_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"响应结果: {result}")
        else:
            logger.error(f"请求失败: {response.status_code}, {response.text}")
    except Exception as e:
        logger.error(f"请求时出错: {e}")


if __name__ == "__main__":
    logger.info("开始测试情绪分析MCP服务...")
    
    # 确保服务正在运行
    import time
    time.sleep(2)  # 等待服务启动
    
    test_emotion_mcp_service()
    print("\n" + "="*50 + "\n")
    test_with_sample_payload()
    
    logger.info("测试完成")