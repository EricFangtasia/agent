"""
投资评级模块
"""
import logging
from typing import Dict, Optional
from database.models import News
from sqlalchemy.orm import Session
from ai_analyzer.llm_integration import VolceLLMAnalyzer

from datetime import datetime


class InvestmentRatingSystem:
    """
    投资价值评级系统
    """
    def __init__(self):
        self.llm_analyzer = VolceLLMAnalyzer()
        self.logger = logging.getLogger(__name__)

    def rate_investment_value(self, news: News, cls_subject: str = '') -> Dict[str, any]:
        """
        评估新闻的投资价值
        
        Args:
            news: 新闻对象
            cls_subject: 财联社的主题分类
        """
        try:
            # 使用大模型进行投资价值分析，传入财联社分类
            analysis_result = self.llm_analyzer.analyze_news(news.title, news.content, cls_subject)
            
            if analysis_result:
                return {
                    'investment_rating': analysis_result.get('investment_rating', 5),
                    'investment_type': analysis_result.get('investment_type', '短期'),
                    'is_viral': analysis_result.get('is_viral', False),
                    'industry': analysis_result.get('industry', '其他'),
                    'industry_level': analysis_result.get('industry_level', 'C'),
                    'sector': analysis_result.get('sector', '未分类'),
                    'analysis': analysis_result.get('analysis', '')
                }
            else:
                # 如果大模型分析失败，返回默认值
                return {
                    'investment_rating': 5,
                    'investment_type': '短期',
                    'is_viral': False,
                    'industry': '其他',
                    'industry_level': 'C',
                    'sector': '未分类',
                    'analysis': '分析失败，使用默认评级'
                }
                
        except Exception as e:
            self.logger.error(f"投资价值评估失败: {e}")
            return {
                'investment_rating': 5,
                'investment_type': '短期',
                'is_viral': False,
                'industry': '其他',
                'industry_level': 'C',
                'sector': '未分类',
                'analysis': f'评估过程中发生错误: {e}'
            }

    def update_news_rating(self, news: News, db: Session, cls_subject: str = ''):
        """
        更新新闻的评级信息
        
        Args:
            news: 新闻对象
            db: 数据库会话
            cls_subject: 财联社的主题分类
        """
        try:
            rating_info = self.rate_investment_value(news, cls_subject)
            
            # 更新新闻对象
            news.investment_rating = rating_info['investment_rating']
            news.investment_type = rating_info['investment_type']
            news.is_viral = rating_info['is_viral']
            news.industry = rating_info['industry']
            news.industry_level = rating_info['industry_level']
            news.sector = rating_info['sector']
            news.recommended_industry = rating_info.get('recommended_industry', '')
            news.concepts = rating_info.get('concepts', '')
            news.related_stocks = rating_info.get('related_stocks', '')
            news.ai_summary = rating_info['analysis']
            news.analysis_time = datetime.now()  # 记录AI分析时间
            
            db.commit()
            self.logger.info(f"已更新新闻 {news.id} 的投资评级: {news.investment_rating}, 类型: {news.investment_type}, 行业: {news.industry}({news.industry_level}级)")
            
            return True
        except Exception as e:
            self.logger.error(f"更新新闻评级失败: {e}")
            db.rollback()
            return False

    def categorize_investment_type(self, rating: int) -> str:
        """
        根据评分确定投资类型
        """
        if rating >= 8:
            return "高价值"
        elif rating >= 5:
            return "中等价值"
        else:
            return "低价值"