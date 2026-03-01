# -*- coding: utf-8 -*-
'''
@File    :   news_api_v0.py
@Author  :   新闻API
'''

from fastapi import APIRouter, Query
from typing import Optional
from digitalHuman.utils import logger
import sys
import os

# 添加 crawler 目录到路径
crawler_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
crawler_dir = os.path.join(crawler_dir, 'crawler')
if crawler_dir not in sys.path:
    sys.path.insert(0, crawler_dir)

from database.mysql_manager import NewsDB

router = APIRouter(prefix="/news")

# ========================= 获取新闻列表 ===========================
@router.get("")
async def get_news_list(
    days: int = Query(default=3, description="获取最近N天的新闻"),
    industry: Optional[str] = Query(default=None, description="按行业筛选"),
    limit: int = Query(default=50, description="返回数量限制"),
    playable_only: bool = Query(default=True, description="只返回可播放的新闻")
):
    """获取新闻列表"""
    try:
        db = NewsDB()
        news_list = db.get_recent_news(days=days, industry=industry)
        
        # 过滤不可播放的新闻（抖音直播合规）
        # 必须同时满足：1. 经过AI分析 2. is_playable=1
        if playable_only:
            news_list = [n for n in news_list if 
                         n.get('is_playable', 0) == 1 and 
                         n.get('analyzed_at') is not None]
            logger.info(f"[NEWS API] 过滤后新闻数量: {len(news_list)} (playable_only=True)")
        
        # 限制返回数量
        if news_list and len(news_list) > limit:
            news_list = news_list[:limit]
        
        # 格式化返回数据
        result = []
        for news in news_list:
            result.append({
                "id": news.get('id'),
                "title": news.get('title', ''),
                "content": news.get('content', ''),
                "url": news.get('source_url', ''),
                "publish_time": str(news.get('publish_time', '')),
                "category": news.get('category', ''),
                "source": news.get('source', '财联社'),
                "industry": news.get('industry', ''),
                "industry_level": news.get('industry_level', ''),
                "sector": news.get('sector', ''),
                "is_viral": news.get('is_viral', 0),
                "is_playable": news.get('is_playable', 1),
                "playable_reason": news.get('playable_reason', ''),
                "investment_rating": news.get('investment_rating'),
                "investment_type": news.get('investment_type', ''),
                "analysis": news.get('analysis', '')
            })
        
        return {"code": 200, "data": result, "message": "success"}
    except Exception as e:
        logger.error(f"[NEWS API] get_news_list error: {str(e)}")
        return {"code": 500, "data": [], "message": str(e)}


# ========================= 获取重磅新闻 ===========================
@router.get("/important")
async def get_important_news(
    days: int = Query(default=7, description="获取最近N天的重磅新闻")
):
    """获取重磅新闻"""
    try:
        db = NewsDB()
        news_list = db.get_important_news(days=days)
        
        result = []
        for news in news_list:
            result.append({
                "id": news.get('id'),
                "title": news.get('title', ''),
                "content": news.get('content', ''),
                "url": news.get('source_url', ''),
                "publish_time": str(news.get('publish_time', '')),
                "category": news.get('category', ''),
                "source": news.get('source', '财联社'),
                "industry": news.get('industry', ''),
                "sector": news.get('sector', ''),
                "investment_rating": news.get('investment_rating'),
                "analysis": news.get('analysis', '')
            })
        
        return {"code": 200, "data": result, "message": "success"}
    except Exception as e:
        logger.error(f"[NEWS API] get_important_news error: {str(e)}")
        return {"code": 500, "data": [], "message": str(e)}
