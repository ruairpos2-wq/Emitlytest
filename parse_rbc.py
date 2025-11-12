import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from database import NewsDB
import json
import re
import time
import xml.etree.ElementTree as ET

class RBCParser:
    def __init__(self):
        self.main_url = 'https://www.rbc.ru/'
        self.quote_url = 'https://www.rbc.ru/quote'
        self.search_url = 'https://www.rbc.ru/search/'
        self.rss_urls = [
            'https://rssexport.rbc.ru/rbcnews/news/30/full.rss',
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.rbc.ru/'
        }
        self.keywords = ['сбербанк', 'сбер', 'sber', 'sberbank', 'сбербанка', 'сбербанку']
    
    def matches_keywords(self, text):
        if not text:
            return False
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.keywords)
    
    def parse_rss_feed(self, rss_url, limit=100):
        results = []
        try:
            print(f"Fetching RSS: {rss_url}")
            response = requests.get(rss_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            for item in root.findall('.//item'):
                if len(results) >= limit:
                    break
                
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    desc_elem = item.find('description')
                    date_elem = item.find('pubDate')
                    
                    if title_elem is None or link_elem is None:
                        continue
                    
                    title = title_elem.text
                    url = link_elem.text
                    description = desc_elem.text if desc_elem is not None else ''
                    pub_date = date_elem.text if date_elem is not None else ''
                    
                    if not title or not url:
                        continue
                    
                    if not self.matches_keywords(title) and not self.matches_keywords(description):
                        continue
                    
                    if pub_date:
                        try:
                            from email.utils import parsedate_to_datetime
                            dt = parsedate_to_datetime(pub_date)
                            date_str = dt.strftime('%Y-%m-%d %H:%M')
                        except:
                            date_str = datetime.now().strftime('%Y-%m-%d')
                    else:
                        date_str = datetime.now().strftime('%Y-%m-%d')
                    
                    soup_desc = BeautifulSoup(description, 'html.parser')
                    clean_desc = soup_desc.get_text(strip=True)
                    
                    results.append({
                        'title': title,
                        'content': clean_desc[:500] if clean_desc else title,
                        'date': date_str,
                        'source': 'РБК',
                        'url': url
                    })
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error parsing RSS {rss_url}: {e}")
        
        return results
    
    def parse_article_page(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            content_elem = soup.find('div', class_='article__text')
            if not content_elem:
                content_elem = soup.find('div', {'itemprop': 'articleBody'})
            
            if content_elem:
                paragraphs = content_elem.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
                return content[:400] if content else ''
            return ''
        except:
            return ''
    
    def parse_news(self, query='Сбербанк', limit=5):
        all_results = []
        seen_urls = set()
        
        print(f"=== Starting comprehensive RBC news parsing ===")
        print(f"Target: {limit} articles about {', '.join(self.keywords)}\n")
        
        print("1. Parsing RSS feeds...")
        for rss_url in self.rss_urls:
            rss_results = self.parse_rss_feed(rss_url, limit=200)
            for article in rss_results:
                if article['url'] not in seen_urls:
                    all_results.append(article)
                    seen_urls.add(article['url'])
                    print(f"   ✓ RSS: {article['title'][:60]}...")
        
        print(f"\n2. Parsing quote page...")
        try:
            response = requests.get(self.quote_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = soup.find_all('a', class_='news-feed__item')
            
            print(f"   Found {len(news_items)} items on quote page")
            
            for item in news_items:
                if len(all_results) >= limit * 3:
                    break
                
                try:
                    title_span = item.find('span', class_='news-feed__item__title')
                    if not title_span:
                        continue
                    
                    title = title_span.get_text(strip=True)
                    url = item.get('href', '')
                    
                    if not title or not url or len(title) < 15:
                        continue
                    
                    if not url.startswith('http'):
                        url = f'https://www.rbc.ru{url}'
                    
                    if url in seen_urls:
                        continue
                    
                    if not self.matches_keywords(title):
                        continue
                    
                    seen_urls.add(url)
                    
                    date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
                    if date_match:
                        date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                    else:
                        date_str = datetime.now().strftime('%Y-%m-%d')
                    
                    time_elem = item.find('span', class_='news-feed__item__date-time')
                    time_str = time_elem.get_text(strip=True) if time_elem else ''
                    
                    all_results.append({
                        'title': title,
                        'content': title,
                        'date': f"{date_str} {time_str}".strip(),
                        'source': 'РБК',
                        'url': url
                    })
                    
                    print(f"   ✓ Quote: {title[:60]}...")
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"   Error: {e}")
        
        print(f"\n3. Parsing main page...")
        try:
            response = requests.get(self.main_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = soup.find_all('a', class_='news-feed__item')
            
            print(f"   Found {len(news_items)} items on main page")
            
            for item in news_items:
                if len(all_results) >= limit * 3:
                    break
                
                try:
                    title_span = item.find('span', class_='news-feed__item__title')
                    if not title_span:
                        continue
                    
                    title = title_span.get_text(strip=True)
                    url = item.get('href', '')
                    
                    if not title or not url or len(title) < 15:
                        continue
                    
                    if not url.startswith('http'):
                        url = f'https://www.rbc.ru{url}'
                    
                    if url in seen_urls:
                        continue
                    
                    if not self.matches_keywords(title):
                        continue
                    
                    seen_urls.add(url)
                    
                    date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
                    if date_match:
                        date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                    else:
                        date_str = datetime.now().strftime('%Y-%m-%d')
                    
                    time_elem = item.find('span', class_='news-feed__item__date-time')
                    time_str = time_elem.get_text(strip=True) if time_elem else ''
                    
                    all_results.append({
                        'title': title,
                        'content': title,
                        'date': f"{date_str} {time_str}".strip(),
                        'source': 'РБК',
                        'url': url
                    })
                    
                    print(f"   ✓ Main: {title[:60]}...")
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"   Error: {e}")
        
        all_results.sort(key=lambda x: x['date'], reverse=True)
        results = all_results[:limit]
        
        print(f"\n=== Summary ===")
        print(f"Total unique articles found: {len(all_results)}")
        print(f"Returning top {len(results)} articles")
        
        return results
        
        if len(results) < limit:
            try:
                response = requests.get(self.main_url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                news_items = soup.find_all('a', class_='item__link')
                if not news_items:
                    news_items = soup.find_all('a', href=re.compile(r'/\w+/\d+/\d+/\d+/'))
                
                for item in news_items:
                    if len(results) >= limit:
                        break
                    
                    try:
                        title = item.get_text(strip=True)
                        url = item.get('href', '')
                        
                        if not title or not url or not self.matches_keywords(title):
                            continue
                        
                        full_url = url if url.startswith('http') else f'https://www.rbc.ru{url}'
                        
                        results.append({
                            'title': title,
                            'content': title,
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'source': 'РБК',
                            'url': full_url
                        })
                    except Exception:
                        continue
            except Exception as e:
                print(f"Error fetching from main page: {e}")
        
        return results

def main():
    parser = RBCParser()
    db = NewsDB()
    
    news_list = parser.parse_news()
    print(f"Found {len(news_list)} news from RBC")
    
    for news in news_list:
        db.add_news(
            title=news['title'],
            content=news['content'],
            date=news['date'],
            source=news['source'],
            url=news['url']
        )
    
    print("RBC news saved to database")

if __name__ == '__main__':
    main()
