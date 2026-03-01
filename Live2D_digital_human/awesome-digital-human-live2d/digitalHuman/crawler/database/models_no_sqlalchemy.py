"""
数据库模型（无SQLAlchemy依赖版本）
使用纯mysql-connector-python实现数据库操作
"""
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import logging

class News:
    """
    新闻数据模型
    """
    def __init__(self, title="", content="", source_url="", publish_time=None, 
                 category="", source="", ai_summary=None, accuracy_score=None, 
                 investment_rating=None, investment_type=None, is_viral=False):
        self.id = None
        self.title = title
        self.content = content
        self.source_url = source_url
        self.publish_time = publish_time or datetime.now()
        self.crawl_time = datetime.now()
        self.category = category
        self.source = source
        self.ai_summary = ai_summary
        self.accuracy_score = accuracy_score
        self.investment_rating = investment_rating
        self.investment_type = investment_type
        self.is_viral = is_viral

    @staticmethod
    def create_table(connection):
        """创建新闻表"""
        cursor = connection.cursor()
        try:
            table_sql = """
            CREATE TABLE IF NOT EXISTS news (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                content TEXT NOT NULL,
                source_url VARCHAR(1000),
                publish_time DATETIME,
                crawl_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                category VARCHAR(100),
                source VARCHAR(100),
                ai_summary TEXT,
                accuracy_score FLOAT,
                investment_rating INT,
                investment_type VARCHAR(20),
                is_viral BOOLEAN DEFAULT FALSE
            )
            """
            cursor.execute(table_sql)
            connection.commit()
            logging.info("数据表 news 创建成功或已存在")
        except Error as e:
            logging.error(f"创建news表时出错: {e}")
        finally:
            cursor.close()

    @staticmethod
    def create_accuracy_table(connection):
        """创建准确性验证表"""
        cursor = connection.cursor()
        try:
            table_sql = """
            CREATE TABLE IF NOT EXISTS accuracy_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                news_id INT,
                source_1 VARCHAR(200),
                source_2 VARCHAR(200),
                consistency_score FLOAT,
                verified BOOLEAN DEFAULT FALSE,
                verification_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(table_sql)
            connection.commit()
            logging.info("数据表 accuracy_records 创建成功或已存在")
        except Error as e:
            logging.error(f"创建accuracy_records表时出错: {e}")
        finally:
            cursor.close()

    @staticmethod
    def insert_news(connection, news_obj):
        """插入新闻数据"""
        cursor = connection.cursor()
        try:
            insert_sql = """
            INSERT INTO news (title, content, source_url, publish_time, category, source, crawl_time)
            VALUES (%(title)s, %(content)s, %(source_url)s, %(publish_time)s, %(category)s, %(source)s, %(crawl_time)s)
            """
            
            data = {
                'title': news_obj.title[:500],  # 限制标题长度
                'content': news_obj.content,
                'source_url': news_obj.source_url,
                'publish_time': news_obj.publish_time,
                'category': news_obj.category,
                'source': news_obj.source,
                'crawl_time': news_obj.crawl_time
            }
            
            cursor.execute(insert_sql, data)
            connection.commit()
            news_id = cursor.lastrowid
            logging.info(f"成功插入新闻: {news_obj.title[:50]}...")
            return news_id
        except Error as e:
            logging.error(f"插入新闻数据时出错: {e}")
            return None
        finally:
            cursor.close()

    @staticmethod
    def get_news_by_title(connection, title):
        """根据标题查询新闻，用于去重"""
        cursor = connection.cursor()
        try:
            select_sql = "SELECT id, title FROM news WHERE title = %s LIMIT 1"
            cursor.execute(select_sql, (title,))
            result = cursor.fetchone()
            return result
        except Error as e:
            logging.error(f"查询新闻时出错: {e}")
            return None
        finally:
            cursor.close()


class AccuracyRecord:
    """
    准确性验证记录
    """
    def __init__(self, news_id, source_1="", source_2="", consistency_score=None, verified=False):
        self.id = None
        self.news_id = news_id
        self.source_1 = source_1
        self.source_2 = source_2
        self.consistency_score = consistency_score
        self.verified = verified
        self.verification_time = datetime.now()

    @staticmethod
    def insert_record(connection, record_obj):
        """插入准确性验证记录"""
        cursor = connection.cursor()
        try:
            insert_sql = """
            INSERT INTO accuracy_records (news_id, source_1, source_2, consistency_score, verified, verification_time)
            VALUES (%(news_id)s, %(source_1)s, %(source_2)s, %(consistency_score)s, %(verified)s, %(verification_time)s)
            """
            
            data = {
                'news_id': record_obj.news_id,
                'source_1': record_obj.source_1,
                'source_2': record_obj.source_2,
                'consistency_score': record_obj.consistency_score,
                'verified': record_obj.verified,
                'verification_time': record_obj.verification_time
            }
            
            cursor.execute(insert_sql, data)
            connection.commit()
            logging.info(f"成功插入准确性验证记录，新闻ID: {record_obj.news_id}")
            return cursor.lastrowid
        except Error as e:
            logging.error(f"插入准确性验证记录时出错: {e}")
            return None
        finally:
            cursor.close()