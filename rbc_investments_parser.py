#!/usr/bin/env python3
"""
Парсер инвестиционных новостей РБК
Получает последние новости из разделов инвестиций и финансов (без привязки к Сбербанку)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re
from typing import List, Dict
import xml.etree.ElementTree as ET


class RBCInvestmentsParser:
    """Парсер инвестиционных новостей РБК"""
    
    # RSS-ленты для инвестиций
    RSS_FEEDS = [
        "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
        "https://rssexport.rbc.ru/rbcnews/business/30/full.rss",
        "https://rssexport.rbc.ru/rbcnews/economics/30/full.rss",
    ]
    
    # Рубрики для HTML-парсинга
    HTML_SECTIONS = [
        "https://www.rbc.ru/finances/",
        "https://www.rbc.ru/business/",
        "https://www.rbc.ru/economics/",
        "https://www.rbc.ru/money/",
    ]
    
    # Ключевые слова для инвестиционных новостей
    INVESTMENT_KEYWORDS = [
        'инвестиц', 'акци', 'биржа', 'фонд', 'ценные бумаги',
        'облигац', 'дивиденд', 'капитал', 'портфель', 'трейдинг',
        'брокер', 'ipo', 'торги', 'котировк', 'индекс', 'рынок',
        'валют', 'золото', 'нефть', 'газ', 'металл'
    ]
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        }
        self.cutoff_date = datetime.now() - timedelta(days=7)  # Последние 7 дней
        print(f"Ищем инвестиционные статьи начиная с: {self.cutoff_date.strftime('%Y-%m-%d')}")
    
    def _is_investment_news(self, text: str) -> bool:
        """Проверяет, относится ли новость к инвестициям"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.INVESTMENT_KEYWORDS)
    
    def _parse_date(self, date_str: str) -> datetime:
        """Парсит дату из различных форматов"""
        try:
            # RFC 2822 format (RSS)
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            # Убираем timezone info для сравнения
            return dt.replace(tzinfo=None)
        except:
            try:
                # ISO format
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.replace(tzinfo=None)
            except:
                return datetime.now()
    
    def parse_rss_feeds(self) -> List[Dict]:
        """Парсит RSS-ленты РБК"""
        results = []
        
        for feed_url in self.RSS_FEEDS:
            print(f"\n🔍 Проверка RSS: {feed_url}")
            
            try:
                response = requests.get(feed_url, headers=self.headers, timeout=10)
                
                if response.status_code == 404:
                    print(f"  ⚠ RSS недоступен (404)")
                    continue
                    
                response.raise_for_status()
                
                # Парсим XML
                root = ET.fromstring(response.content)
                
                items_count = 0
                found_count = 0
                
                # Ищем элементы item в RSS
                for item in root.findall('.//item'):
                    items_count += 1
                    
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pub_date_elem = item.find('pubDate')
                    description_elem = item.find('description')
                    
                    if title_elem is None or link_elem is None:
                        continue
                    
                    title = title_elem.text
                    url = link_elem.text
                    description = description_elem.text if description_elem is not None else ""
                    
                    # Проверяем дату
                    if pub_date_elem is not None:
                        pub_date = self._parse_date(pub_date_elem.text)
                        if pub_date < self.cutoff_date:
                            continue
                    
                    # Проверяем, относится ли к инвестициям
                    full_text = f"{title} {description}"
                    if self._is_investment_news(full_text):
                        date_str = pub_date.strftime('%Y-%m-%d') if pub_date_elem else datetime.now().strftime('%Y-%m-%d')
                        
                        results.append({
                            'title': title,
                            'url': url,
                            'date': date_str,
                            'source': 'RSS'
                        })
                        found_count += 1
                        print(f"  ✓ [{date_str}] {title[:60]}...")
                
                print(f"  Проверено: {items_count} новостей, найдено инвестиционных: {found_count}")
                time.sleep(1)
                
            except requests.exceptions.Timeout:
                print(f"  ✗ Таймаут соединения")
            except requests.exceptions.RequestException as e:
                print(f"  ✗ Ошибка запроса: {e}")
            except ET.ParseError as e:
                print(f"  ✗ Ошибка парсинга XML: {e}")
        
        return results
    
    def parse_html_sections(self, max_pages: int = 3) -> List[Dict]:
        """Парсит HTML-разделы РБК"""
        results = []
        
        for section_url in self.HTML_SECTIONS:
            print(f"\n🔍 Проверка раздела: {section_url}")
            
            try:
                response = requests.get(section_url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Ищем статьи на странице
                articles = soup.find_all('a', class_=re.compile(r'(item__link|news-feed__item)'))
                
                found_count = 0
                
                for article in articles[:30]:  # Берем первые 30 статей
                    title = article.get_text(strip=True)
                    url = article.get('href', '')
                    
                    if not url.startswith('http'):
                        url = f"https://www.rbc.ru{url}"
                    
                    # Проверяем, относится ли к инвестициям
                    if self._is_investment_news(title):
                        results.append({
                            'title': title,
                            'url': url,
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'source': 'HTML'
                        })
                        found_count += 1
                        print(f"  ✓ {title[:60]}...")
                
                print(f"  Найдено инвестиционных новостей: {found_count}")
                time.sleep(2)  # Задержка между запросами
                
            except requests.exceptions.RequestException as e:
                print(f"  ✗ Ошибка загрузки: {e}")
        
        return results
    
    def parse(self) -> List[Dict]:
        """Основной метод парсинга"""
        print("\n" + "="*70)
        print("ПАРСИНГ ИНВЕСТИЦИОННЫХ НОВОСТЕЙ РБК")
        print("="*70)
        
        # RSS парсинг
        rss_results = self.parse_rss_feeds()
        print(f"\n📰 RSS: найдено {len(rss_results)} инвестиционных статей")
        
        # HTML парсинг
        html_results = self.parse_html_sections()
        print(f"\n🌐 HTML: найдено {len(html_results)} инвестиционных статей")
        
        # Объединяем результаты и удаляем дубликаты
        all_results = rss_results + html_results
        
        # Удаляем дубликаты по URL
        unique_results = []
        seen_urls = set()
        
        for result in all_results:
            if result['url'] not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result['url'])
        
        print(f"\n✅ Итого уникальных инвестиционных новостей: {len(unique_results)}")
        
        return unique_results


def main():
    """Тестовый запуск парсера"""
    parser = RBCInvestmentsParser()
    results = parser.parse()
    
    print("\n" + "="*70)
    print("ПРИМЕРЫ НАЙДЕННЫХ НОВОСТЕЙ")
    print("="*70)
    
    for i, news in enumerate(results[:5], 1):
        print(f"\n{i}. [{news['date']}] {news['title']}")
        print(f"   {news['url']}")


if __name__ == '__main__':
    main()
