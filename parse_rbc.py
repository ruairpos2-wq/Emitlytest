import requests
from bs4 import BeautifulSoup
from datetime import datetime
from database import NewsDB

class RBCParser:
    def __init__(self):
        self.base_url = 'https://www.rbc.ru/search/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def parse_news(self, query='Сбербанк', limit=5):
        results = []
        try:
            params = {'query': query}
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = soup.select('.search-item')[:limit]
            
            for item in news_items:
                try:
                    title_elem = item.select_one('.search-item__title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    
                    content_elem = item.select_one('.search-item__text')
                    content = content_elem.get_text(strip=True) if content_elem else ''
                    
                    date_elem = item.select_one('.search-item__date')
                    date_str = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')
                    
                    results.append({
                        'title': title,
                        'content': content,
                        'date': date_str,
                        'source': 'РБК',
                        'url': url
                    })
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching RBC news: {e}")
        
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
