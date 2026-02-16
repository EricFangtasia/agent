#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
情绪分析MCP服务客户端示例
"""
import requests
import base64
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 服务地址
SERVICE_URL = "http://localhost:8089"


def get_service_manifest():
    """
    获取服务清单
    """
    try:
        response = requests.get(f"{SERVICE_URL}/manifest")
        if response.status_code == 200:
            manifest = response.json()
            logger.info("服务清单获取成功:")
            print(json.dumps(manifest, indent=2, ensure_ascii=False))
            return manifest
        else:
            logger.error(f"获取服务清单失败: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"请求服务清单时出错: {e}")
        return None


def analyze_image(image_path):
    """
    分析图片情绪
    """
    try:
        # 读取图片并转换为base64
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # 构造请求
        payload = {
            "image_base64": image_base64
        }
        
        # 发送请求
        response = requests.post(
            f"{SERVICE_URL}/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info("情绪分析成功:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        else:
            logger.error(f"情绪分析失败: {response.status_code}")
            logger.error(f"响应内容: {response.text}")
            return None
    except Exception as e:
        logger.error(f"分析图片时出错: {e}")
        return None


def check_health():
    """
    检查服务健康状况
    """
    try:
        response = requests.get(f"{SERVICE_URL}/health")
        if response.status_code == 200:
            health_status = response.json()
            logger.info(f"服务健康状况: {health_status}")
            return health_status
        else:
            logger.error(f"健康检查失败: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"健康检查请求时出错: {e}")
        return None


def main():
    """
    主函数，演示如何使用情绪分析MCP服务
    """
    print("情绪分析MCP服务客户端示例")
    print("=" * 50)
    
    # 检查服务健康状况
    print("\n1. 检查服务健康状况:")
    check_health()
    
    # 获取服务清单
    print("\n2. 获取服务清单:")
    get_service_manifest()
    
    # 分析图片（用户需要提供图片路径）
    print("\n3. 分析图片情绪:")
    image_path = input("请输入要分析的图片路径 (或直接回车跳过): ").strip()
    
    if image_path:
        analyze_image(image_path)
    else:
        print("跳过图片分析步骤")
    
    print("\n客户端示例执行完成")


if __name__ == "__main__":
    main()