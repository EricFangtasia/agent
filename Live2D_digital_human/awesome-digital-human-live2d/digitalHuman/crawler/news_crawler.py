"""
新闻爬虫主模块（标准库版本）
使用Python标准库实现，无需安装requests库
"""
import time
from datetime import datetime, date
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, urlencode
import logging
import re
import urllib.request
import urllib.error
from http import cookiejar
import gzip
import zlib
import json

from bs4 import BeautifulSoup  # 我们仍然需要BeautifulSoup进行HTML解析

# 导入敏感词过滤模块
import sys
import os
utils_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
utils_dir = os.path.join(utils_dir, 'utils')
if utils_dir not in sys.path:
    sys.path.insert(0, utils_dir)
from douyin_filter import filter_text_for_douyin

# 直接定义常量，而不是从settings导入
CRAWLER_DELAY = 1  # 爬取间隔（秒）
MAX_RETRIES = 3  # 最大重试次数
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

class NewsCrawlerStdLib:
    """
    财联社新闻爬虫类（标准库版本）
    使用Python标准库实现HTTP请求，无需安装requests库
    """
    def __init__(self):
        # 设置cookie jar来处理cookies
        cookie_handler = cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_handler))
        
        # 设置headers
        self.opener.addheaders = [('User-Agent', USER_AGENT)]
        
        self.logger = logging.getLogger(__name__)

    def get_page(self, url: str):
        """
        使用urllib获取网页内容，带重试机制
        """
        for attempt in range(MAX_RETRIES):
            try:
                self.logger.info(f"正在请求: {url}, 尝试次数: {attempt + 1}")
                
                req = urllib.request.Request(url)
                req.add_header('User-Agent', USER_AGENT)
                req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
                req.add_header('Accept-Language', 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2')
                req.add_header('Accept-Encoding', 'gzip, deflate')
                req.add_header('Connection', 'keep-alive')
                req.add_header('Upgrade-Insecure-Requests', '1')
                
                response = self.opener.open(req, timeout=REQUEST_TIMEOUT)
                content = response.read()
                
                # 检查是否是压缩内容并解压
                if response.info().get('Content-Encoding') == 'gzip':
                    content = gzip.decompress(content)
                elif response.info().get('Content-Encoding') == 'deflate':
                    try:
                        content = zlib.decompress(content, -zlib.MAX_WBITS)
                    except zlib.error:
                        # 如果不是zlib格式，尝试inflate
                        content = zlib.decompress(content)
                
                # 尝试解码
                try:
                    content = content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        content = content.decode('gbk')
                    except UnicodeDecodeError:
                        content = content.decode('utf-8', errors='ignore')
                
                return content
            except urllib.error.HTTPError as e:
                self.logger.warning(f"HTTP错误 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                if e.code == 404:
                    break  # 404错误不需要重试
                time.sleep(CRAWLER_DELAY * (attempt + 1))
            except urllib.error.URLError as e:
                self.logger.warning(f"URL错误 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                time.sleep(CRAWLER_DELAY * (attempt + 1))
            except UnicodeDecodeError as e:
                self.logger.warning(f"解码错误 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                time.sleep(CRAWLER_DELAY * (attempt + 1))
            except Exception as e:
                self.logger.warning(f"其他错误 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                time.sleep(CRAWLER_DELAY * (attempt + 1))
        
        self.logger.error(f"在 {MAX_RETRIES} 次尝试后仍无法获取 {url}")
        return None

    def get_api_data(self, last_time: int = None) -> List[Dict[str, str]]:
        """
        从页面HTML中解析__NEXT_DATA__获取新闻数据
        """
        # 先获取电报页面
        page_url = "https://www.cls.cn/telegraph"
        
        try:
            content = self.get_page(page_url)
            if not content:
                self.logger.error("无法获取页面内容")
                return []
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # 查找__NEXT_DATA__ script标签
            next_data_script = soup.find('script', id='__NEXT_DATA__', type='application/json')
            
            if not next_data_script:
                self.logger.warning("未找到__NEXT_DATA__标签，尝试从页面解析新闻列表")
                return self._parse_html_news_list(soup)
            
            try:
                import json
                data = json.loads(next_data_script.string)
                
                # 解析新闻数据
                news_list = []
                props = data.get('props', {})
                initial_state = props.get('initialState', {})
                telegraph = initial_state.get('telegraph', {})
                telegraph_list = telegraph.get('telegraphList', [])
                
                if not telegraph_list:
                    self.logger.warning("telegraphList为空，尝试备用路径")
                    # 尝试其他可能的数据路径
                    page_data = props.get('pageProps', {})
                    telegraph_list = page_data.get('telegraphList', [])
                
                for item in telegraph_list:
                    try:
                        item_time = datetime.fromtimestamp(item.get('ctime', 0))
                        
                        # 获取分类
                        subjects = item.get('subjects', [])
                        category = subjects[0].get('subject_name', '快讯') if subjects else '快讯'
                        
                        # 获取原始标题和内容（过滤前）
                        origin_title = item.get('title', '')
                        origin_content = item.get('content', '')
                        
                        # 敏感词过滤（财联社→财经社，保留日期格式）
                        title = filter_text_for_douyin(origin_title)
                        content = filter_text_for_douyin(origin_content)
                        
                        news_item = {
                            'title': title,
                            'content': content,
                            'origin_title': origin_title,
                            'origin_content': origin_content,
                            'url': f"https://www.cls.cn/detail/{item.get('id', '')}",
                            'publish_time': item_time,
                            'category': category,
                            'source': '财联社'
                        }
                        news_list.append(news_item)
                    except Exception as e:
                        self.logger.warning(f"解析新闻项失败: {e}")
                        continue
                
                self.logger.info(f"从__NEXT_DATA__解析到 {len(news_list)} 条新闻")
                return news_list
                
            except json.JSONDecodeError as e:
                self.logger.error(f"解析__NEXT_DATA__ JSON失败: {e}")
                return self._parse_html_news_list(soup)
                
        except Exception as e:
            self.logger.error(f"获取页面数据失败: {e}")
            return []
    
    def _parse_html_news_list(self, soup) -> List[Dict[str, str]]:
        """
        备用方法：从HTML中解析新闻列表
        """
        news_list = []
        
        try:
            # 查找新闻条目
            news_items = soup.find_all('div', class_=re.compile(r'telegraph-item|news-item|article-item'))
            
            for item in news_items:
                try:
                    title_elem = item.find(['h1', 'h2', 'h3', 'h4'])
                    origin_title = title_elem.get_text().strip() if title_elem else ''
                    
                    content_elem = item.find('p') or item.find('div', class_=re.compile(r'content|text'))
                    origin_content = content_elem.get_text().strip() if content_elem else ''
                    
                    # 敏感词过滤（财联社→财经社，保留日期格式）
                    title = filter_text_for_douyin(origin_title)
                    content = filter_text_for_douyin(origin_content)
                    
                    link_elem = item.find('a', href=True)
                    href = link_elem['href'] if link_elem else ''
                    
                    if title or content:
                        full_url = urljoin('https://www.cls.cn', href) if href else ''
                        news_list.append({
                            'title': title,
                            'content': content,
                            'origin_title': origin_title,
                            'origin_content': origin_content,
                            'url': full_url,
                            'publish_time': datetime.now(),
                            'category': '快讯',
                            'source': '财联社'
                        })
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.logger.error(f"HTML解析失败: {e}")
        
        return news_list

    def parse_news_list(self, base_url: str) -> List[Dict[str, str]]:
        """
        解析新闻列表页面，提取新闻链接
        """
        content = self.get_page(base_url)
        if not content:
            return []

        soup = BeautifulSoup(content, 'html.parser')
        news_links = []

        # 尝试多种方式找到新闻链接
        # 1. 查找所有包含新闻路径的链接
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # 财联社快讯页面的链接模式
            if '/telegraph' in href or '/detail' in href or '/article' in href:
                full_url = urljoin(base_url, href)
                title = link.get_text().strip()
                
                if title and len(title) > 5:  # 确保标题有意义
                    news_links.append({
                        'url': full_url,
                        'title': title
                    })

        # 2. 查找页面中的新闻条目
        news_selectors = [
            '.news-item', '.telegraph-item', '.article-item', 
            '[class*="news"]', '[class*="telegraph"]', '[class*="article"]'
        ]
        
        for selector in news_selectors:
            items = soup.select(selector)
            for item in items:
                # 尝试找到标题和链接
                title_elem = item.find('h1') or item.find('h2') or item.find('h3') or item.find('a')
                if title_elem:
                    title = title_elem.get_text().strip()
                    if not title:
                        continue
                    
                    link_elem = item.find('a', href=True)
                    if link_elem:
                        full_url = urljoin(base_url, link_elem['href'])
                        news_links.append({
                            'url': full_url,
                            'title': title
                        })

        # 3. 查找可能的分页链接
        pagination_links = []
        pagination_selectors = ['.pagination a', '.next-page', '.page-numbers a']
        for selector in pagination_selectors:
            page_links = soup.select(selector)
            for link in page_links:
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    pagination_links.append(full_url)
        
        # 如果找到分页链接，获取更多页面的新闻
        for page_url in pagination_links[:3]:  # 只获取前3页
            self.logger.info(f"获取分页内容: {page_url}")
            page_content = self.get_page(page_url)
            if page_content:
                page_soup = BeautifulSoup(page_content, 'html.parser')
                
                # 在分页中查找新闻链接
                for link in page_soup.find_all('a', href=True):
                    href = link['href']
                    
                    # 财联社快讯页面的链接模式
                    if '/telegraph' in href or '/detail' in href or '/article' in href:
                        full_url = urljoin(base_url, href)
                        title = link.get_text().strip()
                        
                        if title and len(title) > 5:  # 确保标题有意义
                            # 检查是否已存在此链接
                            if not any(l['url'] == full_url for l in news_links):
                                news_links.append({
                                    'url': full_url,
                                    'title': title
                                })

        # 去重
        unique_links = []
        seen_urls = set()
        for link in news_links:
            if link['url'] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link['url'])
        
        return unique_links

    def is_news_detail_link(self, href: str) -> bool:
        """
        判断是否为新闻详情页链接
        """
        # 根据财联社URL模式调整
        news_pattern = re.compile(r'/(\d{4}/\d{2}/\d{2}/\d+\.html|news/\d+|article/\d+|detail/\d+)')
        return bool(news_pattern.search(href))

    def parse_news_content(self, url: str) -> Optional[Dict[str, str]]:
        """
        解析单个新闻页面内容
        """
        content = self.get_page(url)
        if not content:
            return None

        soup = BeautifulSoup(content, 'html.parser')

        # 根据财联社页面结构调整选择器
        # 示例：提取标题、内容、发布时间等
        try:
            # 提取标题 - 尝试多种可能的标题选择器
            title_selectors = ['h1', 'title', '.article-title', '.news-title', '.title']
            title = ""
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    if title:
                        break
            
            if not title:
                # 尝试从页面的其他地方获取标题
                title = soup.find('meta', attrs={'property': 'og:title'})
                if title:
                    title = title.get('content', '').strip()
            
            if not title:
                title = "未找到标题"

            # 提取新闻内容 - 尝试多种可能的内容选择器
            content_selectors = [
                '.article-content', '.news-content', '.content', 
                '.detail-body', '#articleContent', '.article-body',
                '[class*="content"]', '[class*="article"]', '[class*="detail"]'
            ]
            
            content_text = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content_text = content_elem.get_text().strip()
                    if len(content_text) > 20:  # 确保内容足够长
                        break
            
            if not content_text:
                # 如果没找到特定选择器，尝试获取所有p标签
                paragraphs = soup.find_all('p')
                content_text = "\n".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 10])

            # 提取发布时间 - 尝试多种可能的时间选择器
            time_selectors = [
                '.publish-time', '.news-time', '.time', 
                '.article-time', '[datetime]', '.date',
                '[class*="time"]', '[class*="date"]'
            ]
            
            publish_time_str = ""
            for selector in time_selectors:
                time_elem = soup.select_one(selector)
                if time_elem:
                    time_text = time_elem.get_text().strip()
                    if time_text:
                        publish_time_str = time_text
                        break
            
            # 尝试解析时间字符串
            publish_time = self.parse_time_string(publish_time_str) if publish_time_str else datetime.now()

            # 提取分类信息
            category = self.extract_category(soup)

            return {
                'title': title,
                'content': content_text,
                'url': url,
                'publish_time': publish_time,
                'category': category,
                'source': '财联社'
            }
        except Exception as e:
            self.logger.error(f"解析新闻内容失败 {url}: {e}")
            return None

    def parse_time_string(self, time_str: str) -> Optional[datetime]:
        """
        解析时间字符串
        """
        # 根据财联社时间格式调整
        time_str = time_str.strip()
        patterns = [
            '%Y-%m-%d %H:%M',  # 2023-01-01 12:30
            '%Y-%m-%d %H:%M:%S',  # 2023-01-01 12:30:45
            '%Y/%m/%d %H:%M',  # 2023/01/01 12:30
            '%Y年%m月%d日 %H:%M',  # 2023年01月01日 12:30
            '%m-%d %H:%M',  # 01-01 12:30
            '%m/%d %H:%M',  # 01/01 12:30
        ]
        
        for pattern in patterns:
            try:
                if '%m-%d' in pattern or '%m/%d' in pattern:
                    # 如果时间字符串只包含月日，则加上今年
                    year = datetime.now().year
                    formatted_time_str = f"{year}-{time_str.replace('/', '-').replace('年','-').replace('月','-').replace('日','')}"
                    full_pattern = f"%Y-{pattern.lstrip('%m')}"
                    return datetime.strptime(formatted_time_str, full_pattern)
                else:
                    return datetime.strptime(time_str, pattern)
            except ValueError:
                continue
        
        # 如果没有匹配的格式，返回当前时间
        return datetime.now()

    def extract_category(self, soup) -> str:
        """
        提取新闻分类
        """
        # 根据财联社页面结构调整
        category_selectors = [
            '.category', '.news-category', '.breadcrumb', 
            '.nav-current', '.channel-name',
            '[class*="category"]', '[class*="tag"]'
        ]
        
        for selector in category_selectors:
            category_elem = soup.select_one(selector)
            if category_elem:
                category = category_elem.get_text().strip()
                if category:
                    return category
        
        return "快讯"

    def crawl_news(self, base_url: str) -> List[Dict[str, str]]:
        """
        爬取新闻 - 结合API和HTML解析两种方式
        """
        self.logger.info(f"开始爬取新闻: {base_url}")
        
        # 首先尝试使用API方式获取数据
        api_news = self.get_api_data()
        self.logger.info(f"通过API获取到 {len(api_news)} 条新闻")
        
        # 然后使用HTML解析方式获取数据
        html_news = []
        news_links = self.parse_news_list(base_url)
        self.logger.info(f"通过HTML解析找到 {len(news_links)} 个新闻链接")

        for i, link_info in enumerate(news_links[:50]):  # 处理前50个链接
            self.logger.info(f"正在处理新闻 {i+1}/{min(len(news_links), 50)}: {link_info['title'][:50]}...")
            
            # 解析新闻内容
            news_data = self.parse_news_content(link_info['url'])
            if news_data:
                html_news.append(news_data)
            
            # 控制爬取频率
            if i < len(news_links) - 1:
                time.sleep(CRAWLER_DELAY)
        
        self.logger.info(f"通过HTML解析获取到 {len(html_news)} 条新闻")
        
        # 合并API和HTML获取的数据
        all_news = api_news + html_news
        
        self.logger.info(f"完成爬取，共获取 {len(all_news)} 篇新闻")
        return all_news

    def crawl_single_news(self, url: str) -> Optional[Dict[str, str]]:
        """
        爬取单个新闻
        """
        return self.parse_news_content(url)