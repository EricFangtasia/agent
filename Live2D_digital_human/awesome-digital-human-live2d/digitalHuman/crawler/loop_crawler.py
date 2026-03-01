"""
财经新闻定时爬取脚本
定时从财联社获取新闻并保存到数据库，然后进行 AI 分析
"""
import logging
import time
import sys
import os

# 添加当前目录到路径（crawler 目录）
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from news_crawler import NewsCrawlerStdLib
from database.mysql_manager import NewsDB

# 尝试导入 AI 分析器
try:
    from ai_analyzer.llm_integration import VolceLLMAnalyzer
    AI_ANALYZER_AVAILABLE = True
except ImportError:
    AI_ANALYZER_AVAILABLE = False
    print("警告：AI 分析器不可用，请检查配置")


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def crawl_and_save(days=1):
    """爬取并保存新闻到数据库"""
    logger = logging.getLogger(__name__)
    
    # 初始化爬虫和数据库
    crawler = NewsCrawlerStdLib()
    db = NewsDB()
    
    logger.info(f"开始爬取最近 {days} 天的财经新闻...")
    
    # 爬取新闻（传入财联社首页URL）
    base_url = "https://www.cls.cn/telegraph"
    news_list = crawler.crawl_news(base_url)
    
    if not news_list:
        logger.warning("未获取到任何新闻数据")
        return False
    
    logger.info(f"成功获取 {len(news_list)} 条新闻")
    
    # 保存到数据库
    inserted = db.insert_news(news_list)
    logger.info(f"成功插入 {inserted} 条新闻到数据库")
    
    return True


def analyze_news(limit: int = 5):
    """对未分析的新闻进行 AI 分析
    
    Args:
        limit: 每次分析的新闻数量上限，默认5条（节省token）
    """
    if not AI_ANALYZER_AVAILABLE:
        print("AI 分析器不可用，跳过分析")
        return
    
    logger = logging.getLogger(__name__)
    db = NewsDB()
    
    # 初始化 AI 分析器
    try:
        analyzer = VolceLLMAnalyzer()
    except Exception as e:
        logger.error(f"AI 分析器初始化失败：{e}")
        return
    
    # 获取未分析的新闻
    news_to_analyze = db.get_news_for_analysis(limit=limit)
    
    if not news_to_analyze:
        logger.info("没有需要分析的新闻")
        return
    
    logger.info(f"开始分析 {len(news_to_analyze)} 条新闻...")
    
    for news in news_to_analyze:
        try:
            result = analyzer.analyze_news(
                news['title'],
                news['content'],
                news.get('category', '')
            )
            
            if result:
                db.update_analysis(news['title'], result)
                logger.info(f"分析完成：{news['title'][:30]}...")
            else:
                logger.warning(f"分析失败：{news['title'][:30]}...")
            
            # 避免 API 调用过快
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"分析新闻时出错：{e}")
            continue


def main():
    """主函数，循环爬取并分析"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 检查数据库
    if NewsDB is None:
        logger.error("数据库模块不可用，请安装 pymysql: pip install pymysql")
        print("错误：数据库模块不可用，请安装 pymysql: pip install pymysql")
        return
    
    logger.info("财经新闻定时爬取系统启动")
    print("财经新闻定时爬取系统启动，按 Ctrl+C 停止程序")
    print(f"数据库类型：mysql")
    print(f"AI 分析功能：{'启用' if AI_ANALYZER_AVAILABLE else '禁用'}")
    
    # 爬取间隔（秒）
    crawl_interval = 60  # 1 分钟爬取一次
    
    # AI 分析间隔：每 N 次爬取才分析一次（节省 token）
    analyze_interval = 5  # 每 5 次爬取分析一次（约每 5 分钟）
    # 每次分析的新闻数量
    analyze_limit = 5  # 每次最多分析5条新闻（节省token）
    crawl_count = 0
    
    try:
        while True:
            crawl_count += 1
            logger.info(f"=== 第 {crawl_count} 次爬取 ===")
            crawl_and_save(days=1)
            
            # 只在指定间隔时执行 AI 分析
            if AI_ANALYZER_AVAILABLE and crawl_count % analyze_interval == 0:
                logger.info(f"=== 执行 AI 分析（每次最多 {analyze_limit} 条）===")
                analyze_news(limit=analyze_limit)
            elif AI_ANALYZER_AVAILABLE:
                logger.info(f"跳过 AI 分析（下次在第 {analyze_interval - (crawl_count % analyze_interval)} 次爬取时执行）")
            
            logger.info(f"等待 {crawl_interval} 秒后继续...")
            time.sleep(crawl_interval)
            
    except KeyboardInterrupt:
        logger.info("系统被用户中断")
        print("\n程序已停止")
    except Exception as e:
        logger.error(f"主程序异常：{e}")
    finally:
        logger.info("系统关闭")


if __name__ == "__main__":
    main()
