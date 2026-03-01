"""
火山引擎大模型集成 - 使用requests库（避免SDK安装问题）
"""
import requests
import json
import logging
import os
from typing import Dict, Any, Optional
import sys
import os

# 确保 crawler 目录在 sys.path 中
crawler_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if crawler_dir not in sys.path:
    sys.path.insert(0, crawler_dir)

# 直接导入 settings 模块（避免与其他 config 模块冲突）
import config.settings as settings

ARK_API_KEY = settings.ARK_API_KEY
ARK_BASE_URL = settings.ARK_BASE_URL
MODEL_NAME = settings.MODEL_NAME
LLM_TEMPERATURE = settings.LLM_TEMPERATURE
LLM_MAX_TOKENS = settings.LLM_MAX_TOKENS
LLM_TOP_P = settings.LLM_TOP_P

class VolceLLMAnalyzer:
    """
    火山引擎大模型集成类 - 使用requests库
    """
    def __init__(self, model_name: Optional[str] = None):
        self.api_key = ARK_API_KEY
        self.base_url = ARK_BASE_URL
        self.model_name = model_name or MODEL_NAME
        self.temperature = LLM_TEMPERATURE
        self.max_tokens = LLM_MAX_TOKENS
        self.top_p = LLM_TOP_P
        self.logger = logging.getLogger(__name__)

        # 禁用代理以避免连接问题
        os.environ['NO_PROXY'] = '*'
        os.environ['HTTP_PROXY'] = ''
        os.environ['HTTPS_PROXY'] = ''

        if not self.api_key:
            raise ValueError("请设置 ARK_API_KEY 环境变量")

        if not self.model_name:
            raise ValueError("请设置 MODEL_NAME 环境变量")
        
        # 创建session并禁用代理
        self.session = requests.Session()
        self.session.trust_env = False
        
        self.logger.info(f"✓ 火山引擎客户端初始化成功 - 模型: {self.model_name}")

    def analyze_news(self, news_title: str, news_content: str, cls_subject: str = '') -> Optional[Dict[str, Any]]:
        """
        分析新闻内容，获取投资价值评估
        
        Args:
            news_title: 新闻标题
            news_content: 新闻内容
            cls_subject: 财联社的主题分类，如果有则优先使用
        """
        prompt = self._create_analysis_prompt(news_title, news_content, cls_subject)
        
        try:
            response = self._call_llm_api(prompt)
            if response:
                return self._parse_llm_response(response)
            return None
        except Exception as e:
            self.logger.error(f"新闻分析失败: {e}")
            return None

    def _create_analysis_prompt(self, title: str, content: str, cls_subject: str = '') -> str:
        """
        创建分析提示词（精简版，节省token）
        """
        subject_hint = f" 原始分类:{cls_subject}" if cls_subject else ""
        
        prompt = f"""分析以下财经新闻，返回JSON格式结果。

标题: {title}
内容: {content}{subject_hint}

判断要求:
1. is_playable: 是否适合抖音直播(避免涉政/涉军/负面/敏感内容)
2. is_viral: 是否重磅新闻
3. investment_rating: 投资价值1-10分
4. investment_type: 短期或长期
5. industry: 行业(金融/科技/消费/医药/工业/新能源/房地产/农业/宏观经济/交通运输/其他)
6. industry_level: A/B/C/D
7. sector: 细分板块
8. analysis: 简要分析(50字内)

返回JSON:
{{"is_playable":true,"is_viral":false,"investment_rating":5,"investment_type":"短期","industry":"科技","industry_level":"A","sector":"人工智能","analysis":"简要分析内容"}}
"""
        return prompt

    def _call_llm_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        调用火山引擎大模型API - 使用requests库
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一位专业的财经分析师，擅长评估新闻的投资价值和市场影响。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": self.top_p
            }
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60,  # 增加超时时间到60秒
                proxies={}  # 显式禁用代理
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                self.logger.error(f"API调用失败: {response.status_code}, {response.text}")
                return None
            
        except Exception as e:
            self.logger.error(f"API调用异常: {e}")
            return None

    def _parse_llm_response(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        解析大模型响应
        """
        try:
            content = response['choices'][0]['message']['content']
            
            # 尝试提取JSON部分
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                
                # 设置默认值
                result.setdefault('is_playable', False)
                result.setdefault('is_viral', False)
                result.setdefault('playable_reason', '')
                result.setdefault('investment_rating', 5)
                result.setdefault('investment_type', '短期')
                result.setdefault('industry', '其他')
                result.setdefault('industry_level', 'B')
                result.setdefault('sector', '')
                result.setdefault('recommended_industry', '')
                result.setdefault('concepts', '')
                result.setdefault('related_stocks', '')
                result.setdefault('accuracy_score', 80)
                result.setdefault('analysis', '')
                
                return result
            else:
                self.logger.error(f"无法从响应中提取JSON: {content}")
                return None
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger.error(f"解析响应失败: {e}, 原始内容: {response}")
            return None