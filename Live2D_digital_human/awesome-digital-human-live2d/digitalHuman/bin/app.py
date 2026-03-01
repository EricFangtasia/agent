# -*- coding: utf-8 -*-
'''
@File    :   app.py
@Author  :   一力辉 
'''

import uvicorn
from digitalHuman.engine import EnginePool
from digitalHuman.agent import AgentPool
from digitalHuman.server import app
from digitalHuman.utils import config

__all__ = ["runServer"]

def runServer():
    enginePool = EnginePool()
    enginePool.setup(config.SERVER.ENGINES)
    agentPool = AgentPool()
    agentPool.setup(config.SERVER.AGENTS)
    
    # 启动爬虫后台任务（可选）
    import threading
    def start_crawler():
        try:
            # 添加 crawler 目录到路径
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            crawler_dir = os.path.join(os.path.dirname(current_dir), 'crawler')
            sys.path.insert(0, crawler_dir)
            
            from loop_crawler import main as crawler_main
            print("\n[财经爬虫] 启动定时爬取任务...")
            crawler_main()
        except Exception as e:
            print(f"[财经爬虫] 启动失败：{e}")
            import traceback
            traceback.print_exc()
    
    # 在后台线程启动爬虫（非阻塞）
    crawler_thread = threading.Thread(target=start_crawler, daemon=True)
    crawler_thread.start()
    
    # 启动 Web 服务
    uvicorn.run(app, host=config.SERVER.IP, port=config.SERVER.PORT, log_level="info")