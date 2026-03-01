# 数据库模块
"""
MySQL数据库管理器
用于将爬取的新闻数据存储到MySQL数据库
"""
import pymysql
from datetime import datetime, timedelta
import logging
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from config.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
except ImportError:
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "news_analysis_db")


class NewsDB:
    """新闻数据库管理器 - 使用 MySQL"""

    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        self.host = host or MYSQL_HOST
        self.port = port or MYSQL_PORT
        self.user = user or MYSQL_USER
        self.password = password or MYSQL_PASSWORD
        self.database = database or MYSQL_DATABASE
        self.logger = logging.getLogger(__name__)
        self._init_db()

    def _get_connection(self):
        """获取数据库连接"""
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def _init_db(self):
        """初始化数据库表"""
        # 先创建数据库（如果不存在）
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            charset='utf8mb4'
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            conn.commit()
        finally:
            conn.close()

        # 创建表
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS news (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(500) NOT NULL,
                        content TEXT,
                        origin_title VARCHAR(500),
                        origin_content TEXT,
                        source_url VARCHAR(1000),
                        publish_time VARCHAR(50),
                        category VARCHAR(100),
                        source VARCHAR(50) DEFAULT '财联社',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        -- AI分析字段
                        is_viral TINYINT DEFAULT 0,
                        investment_rating INT,
                        investment_type VARCHAR(10),
                        industry VARCHAR(50),
                        industry_level VARCHAR(10),
                        sector VARCHAR(100),
                        analysis TEXT,
                        analyzed_at TIMESTAMP NULL,
                        -- 抖音直播合规
                        is_playable TINYINT DEFAULT 0,
                        playable_reason VARCHAR(500),
                        INDEX idx_publish_time (publish_time),
                        INDEX idx_industry (industry),
                        INDEX idx_is_viral (is_viral),
                        INDEX idx_is_playable (is_playable)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                conn.commit()
                
                # 检查并添加缺失的字段
                try:
                    cursor.execute("SHOW COLUMNS FROM news LIKE 'category'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE news ADD COLUMN category VARCHAR(100) AFTER publish_time")
                        conn.commit()
                        self.logger.info("添加 category 字段")
                except Exception as e:
                    self.logger.warning(f"检查字段失败: {e}")
                
                # 检查 analyzed_at 字段
                try:
                    cursor.execute("SHOW COLUMNS FROM news LIKE 'analyzed_at'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE news ADD COLUMN analyzed_at TIMESTAMP NULL")
                        conn.commit()
                        self.logger.info("添加 analyzed_at 字段")
                except Exception as e:
                    self.logger.warning(f"检查 analyzed_at 字段失败: {e}")
                
                # 检查 source 字段
                try:
                    cursor.execute("SHOW COLUMNS FROM news LIKE 'source'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE news ADD COLUMN source VARCHAR(50) DEFAULT '财联社'")
                        conn.commit()
                        self.logger.info("添加 source 字段")
                except Exception as e:
                    self.logger.warning(f"检查 source 字段失败: {e}")
                
                # 检查 analysis 字段
                try:
                    cursor.execute("SHOW COLUMNS FROM news LIKE 'analysis'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE news ADD COLUMN analysis TEXT")
                        conn.commit()
                        self.logger.info("添加 analysis 字段")
                except Exception as e:
                    self.logger.warning(f"检查 analysis 字段失败: {e}")
                
                # 检查 origin_title 字段
                try:
                    cursor.execute("SHOW COLUMNS FROM news LIKE 'origin_title'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE news ADD COLUMN origin_title VARCHAR(500) AFTER content")
                        conn.commit()
                        self.logger.info("添加 origin_title 字段")
                except Exception as e:
                    self.logger.warning(f"检查 origin_title 字段失败: {e}")
                
                # 检查 origin_content 字段
                try:
                    cursor.execute("SHOW COLUMNS FROM news LIKE 'origin_content'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE news ADD COLUMN origin_content TEXT AFTER origin_title")
                        conn.commit()
                        self.logger.info("添加 origin_content 字段")
                except Exception as e:
                    self.logger.warning(f"检查 origin_content 字段失败: {e}")
                
                # 检查 is_playable 字段
                try:
                    cursor.execute("SHOW COLUMNS FROM news LIKE 'is_playable'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE news ADD COLUMN is_playable TINYINT DEFAULT 0")
                        conn.commit()
                        self.logger.info("添加 is_playable 字段")
                except Exception as e:
                    self.logger.warning(f"检查 is_playable 字段失败: {e}")
                
                # 检查 playable_reason 字段
                try:
                    cursor.execute("SHOW COLUMNS FROM news LIKE 'playable_reason'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE news ADD COLUMN playable_reason VARCHAR(500)")
                        conn.commit()
                        self.logger.info("添加 playable_reason 字段")
                except Exception as e:
                    self.logger.warning(f"检查 playable_reason 字段失败: {e}")
                
                # 检查 recommended_industry 字段
                try:
                    cursor.execute("SHOW COLUMNS FROM news LIKE 'recommended_industry'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE news ADD COLUMN recommended_industry VARCHAR(500)")
                        conn.commit()
                        self.logger.info("添加 recommended_industry 字段")
                except Exception as e:
                    self.logger.warning(f"检查 recommended_industry 字段失败: {e}")
                
                # 检查 concepts 字段
                try:
                    cursor.execute("SHOW COLUMNS FROM news LIKE 'concepts'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE news ADD COLUMN concepts VARCHAR(500)")
                        conn.commit()
                        self.logger.info("添加 concepts 字段")
                except Exception as e:
                    self.logger.warning(f"检查 concepts 字段失败: {e}")
                
                # 检查 related_stocks 字段
                try:
                    cursor.execute("SHOW COLUMNS FROM news LIKE 'related_stocks'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE news ADD COLUMN related_stocks VARCHAR(500)")
                        conn.commit()
                        self.logger.info("添加 related_stocks 字段")
                except Exception as e:
                    self.logger.warning(f"检查 related_stocks 字段失败: {e}")
                
                # 检查 analysis_time 字段
                try:
                    cursor.execute("SHOW COLUMNS FROM news LIKE 'analysis_time'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE news ADD COLUMN analysis_time DATETIME")
                        conn.commit()
                        self.logger.info("添加 analysis_time 字段")
                except Exception as e:
                    self.logger.warning(f"检查 analysis_time 字段失败: {e}")
        finally:
            conn.close()

        self.logger.info(f"MySQL数据库初始化完成：{self.database}")

    def insert_news(self, news_list: list) -> int:
        """插入新闻列表，返回插入数量"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                # 获取已存在的URL和内容（用于去重）
                cursor.execute("SELECT source_url, content FROM news")
                existing_urls = set()
                existing_contents = set()
                for row in cursor.fetchall():
                    if row['source_url']:
                        existing_urls.add(row['source_url'])
                    if row['content']:
                        # 只取前100字符用于内容去重
                        existing_contents.add(row['content'][:100])

                count = 0
                for news in news_list:
                    url = news.get('url', '')
                    content = news.get('content', '')
                    title = news.get('title', '')
                    
                    # 获取原始内容（优先使用爬虫传来的原始值）
                    origin_title = news.get('origin_title', title)
                    origin_content = news.get('origin_content', content)
                    
                    # 去重检查：先检查URL，再检查内容
                    if url and url in existing_urls:
                        continue
                    if content and content[:100] in existing_contents:
                        continue
                    
                    # 如果没有标题，用内容前50字符作为标题
                    if not title:
                        title = content[:50] + '...' if len(content) > 50 else content
                        if not title:
                            title = f"无标题新闻_{datetime.now().strftime('%Y%m%d%H%M%S')}_{count}"
                        if not origin_title:
                            origin_title = title

                    try:
                        cursor.execute('''
                            INSERT INTO news (title, content, origin_title, origin_content, source_url, publish_time, category, source)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            title,
                            content,
                            origin_title,
                            origin_content,
                            url,
                            news.get('publish_time', ''),
                            news.get('category', ''),
                            news.get('source', '财联社')
                        ))
                        if url:
                            existing_urls.add(url)
                        if content:
                            existing_contents.add(content[:100])
                        count += 1
                    except Exception as e:
                        self.logger.error(f"插入新闻失败：{e}")
                        continue

                conn.commit()
        finally:
            conn.close()

        if count > 0:
            self.logger.info(f"成功插入 {count} 条新闻到 MySQL")
        return count

    def update_analysis(self, title: str, analysis_result: dict):
        """更新新闻的 AI 分析结果"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('''
                    UPDATE news SET
                        is_viral = %s,
                        investment_rating = %s,
                        investment_type = %s,
                        industry = %s,
                        industry_level = %s,
                        sector = %s,
                        recommended_industry = %s,
                        concepts = %s,
                        related_stocks = %s,
                        analysis = %s,
                        is_playable = %s,
                        playable_reason = %s,
                        analyzed_at = %s,
                        analysis_time = %s
                    WHERE title = %s
                ''', (
                    1 if analysis_result.get('is_viral') else 0,
                    analysis_result.get('investment_rating', 0),
                    analysis_result.get('investment_type', ''),
                    analysis_result.get('industry', ''),
                    analysis_result.get('industry_level', ''),
                    analysis_result.get('sector', ''),
                    analysis_result.get('recommended_industry', ''),
                    analysis_result.get('concepts', ''),
                    analysis_result.get('related_stocks', ''),
                    analysis_result.get('analysis', ''),
                    1 if analysis_result.get('is_playable', False) else 0,
                    analysis_result.get('playable_reason', ''),
                    now,
                    now,
                    title
                ))
                conn.commit()
                self.logger.info(f"更新分析结果: {title[:30]}... is_playable={analysis_result.get('is_playable', False)}")
        except Exception as e:
            self.logger.error(f"更新分析结果失败：{e}")
        finally:
            conn.close()

    def get_news_for_analysis(self, limit: int = 10) -> list:
        """获取未分析的新闻（analyzed_at 为空且 analysis 为空）"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT id, title, content, category
                    FROM news
                    WHERE analyzed_at IS NULL 
                      AND (analysis IS NULL OR analysis = '')
                    ORDER BY publish_time DESC
                    LIMIT %s
                ''', (limit,))
                return cursor.fetchall()
        finally:
            conn.close()

    def get_recent_news(self, days: int = 7, industry: str = None) -> list:
        """获取最近 N 天的新闻"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                # 计算日期边界
                cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

                query = "SELECT * FROM news WHERE publish_time >= %s"
                params = [cutoff_date]

                if industry:
                    query += " AND industry = %s"
                    params.append(industry)

                query += " ORDER BY publish_time DESC"

                cursor.execute(query, params)
                return cursor.fetchall()
        finally:
            conn.close()

    def get_important_news(self, days: int = 7) -> list:
        """获取重磅新闻"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

                cursor.execute('''
                    SELECT * FROM news
                    WHERE is_viral = 1 AND publish_time >= %s
                    ORDER BY publish_time DESC
                ''', (cutoff_date,))
                return cursor.fetchall()
        finally:
            conn.close()
