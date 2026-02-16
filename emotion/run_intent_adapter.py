#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
情绪分析意图适配器启动脚本
"""
import os
import sys
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_intent_adapter():
    """
    启动情绪分析意图适配器
    """
    try:
        # 添加项目根目录到Python路径
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # 导入并启动意图适配器
        from agent.emotion.emotion_intent_adapter import app
        
        logger.info("情绪分析意图适配器启动中，监听端口: 8090")
        app.run(host='0.0.0.0', port=8090, debug=False)
        
    except Exception as e:
        logger.error(f"启动情绪分析意图适配器时出错: {e}")
        raise


if __name__ == "__main__":
    # 启动服务
    start_intent_adapter()