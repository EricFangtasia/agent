"""
通用工具函数
"""
import re
import logging
import os
from datetime import datetime
from typing import Optional
import hashlib
from config.settings import LOG_LEVEL, LOG_DIR, LOG_FILE

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    设置日志记录器，支持文件和控制台输出
    """
    logger = logging.getLogger(name)
    
    # 设置日志级别
    log_level = getattr(logging, level or LOG_LEVEL, logging.INFO)
    logger.setLevel(log_level)
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 创建日志目录
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        
        # 创建日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        log_file_path = os.path.join(LOG_DIR, LOG_FILE)
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def clean_text(text: str) -> str:
    """
    清理文本，去除多余空白字符
    """
    if not text:
        return ""
    
    # 去除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 去除首尾空白
    text = text.strip()
    return text

def extract_keywords(text: str, max_keywords: int = 10) -> list:
    """
    提取关键词（简化实现）
    """
    if not text:
        return []
    
    # 简单的关键词提取（实际应用中可能需要使用NLP库）
    words = re.findall(r'[\w]{2,}', text)
    
    # 统计词频并返回最常见的词
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1
    
    # 按频率排序并返回前max_keywords个
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]]

def generate_content_hash(content: str) -> str:
    """
    生成内容哈希值，用于检测重复内容
    """
    if not content:
        return ""
    
    # 对内容进行哈希
    content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
    return content_hash

def is_valid_url(url: str) -> bool:
    """
    验证URL是否有效
    """
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return pattern.match(url) is not None

def format_datetime(dt: datetime) -> str:
    """
    格式化日期时间
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S') if dt else None

def safe_int_convert(value, default=0):
    """
    安全地将值转换为整数
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float_convert(value, default=0.0):
    """
    安全地将值转换为浮点数
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default