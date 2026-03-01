"""
准确性验证模块
"""
import logging
from typing import Dict, List, Optional
from database.models import News, AccuracyRecord
from sqlalchemy.orm import Session
from ai_analyzer.prompt_templates import PromptTemplates
from ai_analyzer.llm_integration import VolceLLMAnalyzer

class AccuracyChecker:
    """
    消息准确性验证器
    """
    def __init__(self):
        self.llm_analyzer = VolceLLMAnalyzer()
        self.logger = logging.getLogger(__name__)

    def verify_accuracy(self, news: News, db: Session) -> float:
        """
        验证新闻准确性
        """
        try:
            # 从其他来源获取相关信息进行对比（这里简化处理，实际需要实现多源获取）
            related_sources = self.get_related_sources(news.title, news.content)
            
            if related_sources:
                # 使用大模型进行准确性对比分析
                accuracy_score = self.analyze_accuracy_with_llm(news.content, related_sources)
                
                # 保存准确性记录
                self.save_accuracy_record(news.id, related_sources, accuracy_score, db)
                
                return accuracy_score
            else:
                # 如果没有其他来源，返回原始准确性评分
                return news.accuracy_score or 50.0  # 默认50分
                
        except Exception as e:
            self.logger.error(f"准确性验证失败: {e}")
            return news.accuracy_score or 50.0

    def get_related_sources(self, title: str, content: str) -> List[str]:
        """
        获取相关来源信息（模拟实现，实际需要从其他财经网站获取）
        """
        # 这里应该实现从其他财经网站爬取相关信息的逻辑
        # 为了演示，我们返回一个模拟的来源列表
        # 实际实现需要额外的爬虫逻辑
        
        # 模拟相关来源（实际需要实现真正的多源获取）
        related_sources = [
            f"其他来源报道：{title}的相关信息1",
            f"其他来源报道：{title}的相关信息2"
        ]
        
        return related_sources

    def analyze_accuracy_with_llm(self, original_content: str, related_sources: List[str]) -> float:
        """
        使用大模型分析准确性
        """
        prompt = PromptTemplates.get_accuracy_verification_prompt(original_content, related_sources)
        
        try:
            response = self.llm_analyzer._call_llm_api(prompt)
            if response:
                parsed_response = self.llm_analyzer._parse_llm_response(response)
                if parsed_response and 'accuracy_score' in parsed_response:
                    return float(parsed_response['accuracy_score'])
        except Exception as e:
            self.logger.error(f"使用LLM分析准确性失败: {e}")
        
        # 如果LLM分析失败，返回默认值
        return 50.0

    def save_accuracy_record(self, news_id: int, sources: List[str], accuracy_score: float, db: Session):
        """
        保存准确性记录
        """
        try:
            # 计算一致性评分（简化处理）
            consistency_score = accuracy_score
            
            accuracy_record = AccuracyRecord(
                news_id=news_id,
                source_1=sources[0] if sources else "",
                source_2=sources[1] if len(sources) > 1 else "",
                consistency_score=consistency_score,
                verified=True
            )
            
            db.add(accuracy_record)
            db.commit()
            
            self.logger.info(f"已保存新闻 {news_id} 的准确性记录，评分: {accuracy_score}")
        except Exception as e:
            self.logger.error(f"保存准确性记录失败: {e}")
            db.rollback()