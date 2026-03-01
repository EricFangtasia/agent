"""
项目配置文件
"""
import os

# 火山引擎SDK配置 (使用官方SDK)
ARK_API_KEY = os.getenv("ARK_API_KEY", "5e406c6c-60b1-4842-be32-9b9964068792")  # 火山引擎API密钥
ARK_BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")

# 豆包模型配置
# 注意：根据您的示例，使用的是 doubao-seed-1-8-251228
# 这里列出可用的模型选项
MODEL_NAME = os.getenv("MODEL_NAME", "doubao-seed-2-0-lite-260215")  # 豆包2.0 Lite模型
AVAILABLE_MODELS = {
    "seed-1-8": "doubao-seed-1-8-251228",     # 示例中使用的模型
    "seed-2-pro": "doubao-seed-2.0-pro",      # 豆包2.0 Pro（如果可用）
    "seed-2-lite": "doubao-seed-2.0-lite",    # 豆包2.0 Lite
    "seed-2-mini": "doubao-seed-2.0-mini",    # 豆包2.0 Mini
}

# LLM调用参数
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))  # 控制随机性，0-1之间
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))    # 最大输出token数
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))             # 核采样参数

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./news_analysis.db")

# 爬虫配置
CRAWLER_DELAY = 1  # 爬取间隔（秒）
MAX_RETRIES = 3  # 最大重试次数
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 财联社爬虫URL配置
CLS_BASE_URL = "https://www.cls.cn"
CLS_TELEGRAPH_API = "https://www.cls.cn/nodeapi/updateTelegraphList"  # 电报API

# 定时任务配置
CRAWLING_INTERVAL = 300  # 爬取间隔（秒）

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.getenv("LOG_FILE", "crawler_analysis.log")