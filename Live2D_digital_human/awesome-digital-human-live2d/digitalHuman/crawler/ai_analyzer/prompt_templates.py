"""
提示词模板
"""
class PromptTemplates:
    """
    提示词模板管理类
    """
    
    @staticmethod
    def get_news_analysis_prompt(title: str, content: str) -> str:
        """
        新闻分析提示词模板 - 投资评级 + 抖音直播合规判断
        """
        return f"""
你是一个专业的财经分析师，同时熟悉抖音直播内容合规规范。需要分析以下财经新闻并提供投资价值评估和直播合规判断。

新闻标题：{title}
新闻内容：{content}

请按以下要求进行专业分析：

**1. 抖音直播合规判断**（最重要！）
判断该新闻是否适合在抖音直播间由AI数字人播报：

【绝对不可播放的高风险内容】（is_playable = false）
- 涉政、涉军、涉敏感人物/事件（如：金正恩、伊朗核谈判、俄乌冲突、以色列等）
- 涉突发安全事件（如：爆炸、地震、火车脱轨、重大事故）
- 涉金融证券敏感信息（如：个股评级、股票推荐、清盘呈请、内幕消息）
- 涉政府停摆、政治动荡、领土争端
- 未经证实的负面新闻、谣言
- 涉及领导人、政治敏感词的内容

【可以播放的低风险内容】（is_playable = true）
- 科技产品动态（如：新模型发布、科技产品、星链、机器人）
- 消费与市场（如：票房数据、年货消费、客流统计）
- 气象与民生（如：寒潮预警、大风预警、生活提醒）
- 行业发展动态（如：新能源进展、产业数据）
- 企业正常经营新闻（非负面）

**2. 投资价值评级** (1-10分)
   - 10分：重大政策、大盘走势、重要行业变革
   - 8-9分：重要公司公告、行业龙头动态
   - 5-7分：常规财经数据、中等影响事件
   - 1-4分：例行报道、影响较小

**3. 投资类型划分**
   - 短期：影响1-3个月
   - 中期：影响3-12个月
   - 长期：影响1年以上

**4. 重磅新闻判定**
   - true: 对市场有重大影响
   - false: 常规新闻

**5. 行业分类与分级**
主要行业分类：金融、科技、消费、医药、工业、新能源、房地产、农业、宏观经济、其他
行业级别：A级（国家重点支持）、B级（稳定增长）、C级（传统行业）、D级（面临挑战）

**6. 分析说明**
简要说明判断依据

请严格按以下JSON格式返回（不要添加任何其他内容）：
{{
  "is_playable": true或false,
  "playable_reason": "如果不适合播放，说明具体原因；适合则为空字符串",
  "is_viral": true或false,
  "investment_rating": 1-10,
  "investment_type": "短期"或"中期"或"长期",
  "industry": "所属行业",
  "industry_level": "A"或"B"或"C"或"D",
  "sector": "细分板块",
  "analysis": "分析说明"
}}
"""

    @staticmethod
    def get_accuracy_verification_prompt(news_content: str, sources: list) -> str:
        """
        准确性验证提示词模板
        """
        sources_text = "\n".join([f"来源{i+1}: {source}" for i, source in enumerate(sources)])
        
        return f"""
请对比分析以下多个来源对同一事件的报道，评估原始新闻的准确性：

原始新闻内容：{news_content}

其他来源报道：
{sources_text}

请评估原始新闻的准确性，并提供0-100分的准确性评分，以及简要说明。
返回JSON格式：
{{
  "accuracy_score": 0-100,
  "consistency_analysis": "一致性分析",
  "reliability_assessment": "可靠性评估"
}}
"""

    @staticmethod
    def get_investment_impact_prompt(news_content: str, industry: str) -> str:
        """
        投资影响分析提示词模板
        """
        return f"""
请分析以下新闻对{industry}行业的影响程度和投资机会：

新闻内容：{news_content}

请评估：
1. 对行业的短期影响（1-3个月）
2. 对行业的长期影响（1年以上）
3. 潜在的投资机会
4. 潜在的投资风险

返回JSON格式：
{{
  "short_term_impact": "短期影响分析",
  "long_term_impact": "长期影响分析", 
  "investment_opportunities": "投资机会",
  "investment_risks": "投资风险",
  "recommendation": "投资建议"
}}
"""