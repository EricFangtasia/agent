#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
情绪分析MCP服务启动脚本
"""
import os
import sys
import subprocess
import threading
import time
import logging
from typing import Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def start_mcp_service():
    """
    启动情绪分析MCP服务
    """
    try:
        # 添加项目根目录到Python路径
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # 导入并启动MCP服务
        from agent.emotion.emotion_analysis_mcp_service import app
        
        logger.info("情绪分析MCP服务启动中，监听端口: 8089")
        app.run(host='0.0.0.0', port=8089, debug=False, threaded=True)
        
    except Exception as e:
        logger.error(f"启动情绪分析MCP服务时出错: {e}")
        raise


def test_mcp_service():
    """
    测试MCP服务是否正常运行
    """
    import requests
    
    try:
        response = requests.get("http://localhost:8089/health", timeout=5)
        if response.status_code == 200:
            logger.info("情绪分析MCP服务运行正常")
            return True
        else:
            logger.warning(f"情绪分析MCP服务健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        logger.warning(f"连接情绪分析MCP服务失败: {e}")
        return False


if __name__ == "__main__":
    # 启动服务
    start_mcp_service()