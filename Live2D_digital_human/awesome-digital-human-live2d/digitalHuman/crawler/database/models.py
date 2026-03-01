from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class News(Base):
    """
    新闻数据模型
    """
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), index=True)
    content = Column(Text)
    source_url = Column(String(1000))
    # 时间字段 - 使用本地时间（东8区）
    publish_time = Column(DateTime, default=datetime.now)
    crawl_time = Column(DateTime, default=datetime.now)
    analysis_time = Column(DateTime, default=datetime.now)  # AI分析时间
    
    # AI分析结果
    ai_summary = Column(Text)
    investment_rating = Column(Integer)  # 投资价值评分 1-10
    investment_type = Column(String(20))  # 短期/长期投资
    is_viral = Column(Boolean, default=False)  # 是否为爆款新闻
    
    # 抖音直播合规
    is_playable = Column(Boolean, default=True)  # 是否适合抖音直播播放
    playable_reason = Column(String(500))  # 不适合播放的原因
    
    # 行业分级
    industry = Column(String(100))  # 所属行业
    industry_level = Column(String(20))  # 行业级别: A/B/C/D
    sector = Column(String(100))  # 细分板块
    recommended_industry = Column(String(500))  # 推荐关联行业
    concepts = Column(String(500))  # 相关概念
    related_stocks = Column(String(500))  # 相关股票

class AccuracyRecord(Base):
    """
    准确性验证记录
    """
    __tablename__ = "accuracy_records"

    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer)
    source_1 = Column(String(200))
    source_2 = Column(String(200))
    consistency_score = Column(Float)  # 一致性评分
    verified = Column(Boolean, default=False)
    verification_time = Column(DateTime, default=datetime.utcnow)

# 数据库连接配置
# 可以通过环境变量DATABASE_URL配置数据库连接
# MySQL格式: mysql+pymysql://用户名:密码@主机:端口/数据库名
# SQLite格式: sqlite:///./news_analysis.db

# 默认使用MySQL（使用你提供的配置）
DEFAULT_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/news_analysis_db"

# 如果环境变量未设置，使用默认MySQL配置
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# 创建引擎
if DATABASE_URL.startswith('mysql'):
    # MySQL配置：添加连接池和字符集设置
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # 连接池预检查
        pool_recycle=3600,   # 连接回收时间
        echo=False,          # 不显示SQL语句
        connect_args={
            'charset': 'utf8mb4'
        }
    )
    print(f"✅ 使用MySQL数据库: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else ''}")
else:
    # SQLite配置
    engine = create_engine(DATABASE_URL)
    print(f"✅ 使用SQLite数据库: {DATABASE_URL}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建表
Base.metadata.create_all(bind=engine)