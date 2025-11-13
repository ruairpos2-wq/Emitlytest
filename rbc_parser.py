#!/usr/bin/env python3
"""
Парсер новостей РБК про Сбербанк
Использует RSS-ленты и HTML-парсинг для получения статей за последние 60 дней
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re
from typing import List, Dict
import xml.etree.ElementTree as ET


class RBCParser:
    """Парсер новостей РБК с поддержкой RSS и HTML"""
    
    # RSS-ленты РБК
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
    
    # Ключевые слова для поиска
    KEYWORDS = ['сбербанк', 'сбер', 'sberbank', 'sber']
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        }
        self.cutoff_date = datetime.now() - timedelta(days=60)
        print(f"Ищем статьи начиная с: {self.cutoff_date.strftime('%Y-%m-%d')}")
    
    def _contains_keyword(self, text: str) -> bool:
        """Проверяет наличие ключевых слов в тексте"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.KEYWORDS)
    
    def _parse_date(self, date_str: str) -> datetime:
        """Парсит дату из различных форматов"""
        # Формат RSS: Wed, 13 Nov 2025 12:00:00 +0300
        formats = [
            '%a, %d %b %Y %H:%M:%S %z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%d %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        return datetime.now()
    
    def parse_rss_feeds(self) -> List[Dict]:
        """Парсит RSS-ленты РБК"""
        print("\n[1/2] Парсинг RSS-лент РБК...")
        results = []
        seen_urls = set()
        
        for feed_url in self.RSS_FEEDS:
            try:
                print(f"  Загружаю: {feed_url}")
                response = requests.get(feed_url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"  ⚠ Ошибка {response.status_code}")
                    continue
                
                # Парсим XML
                root = ET.fromstring(response.content)
                items = root.findall('.//item')
                
                for item in items:
                    try:
                        title = item.find('title').text
                        link = item.find('link').text
                        pub_date = item.find('pubDate').text
                        
                        # Проверяем наличие ключевых слов в заголовке
                        if not self._contains_keyword(title):
                            continue
                        
                        # Парсим и проверяем дату
                        date_obj = self._parse_date(pub_date)
                        if date_obj < self.cutoff_date:
                            continue
                        
                        # Избегаем дубликатов
                        if link in seen_urls:
                            continue
                        seen_urls.add(link)
                        
                        results.append({
                            'title': title,
                            'url': link,
                            'date': date_obj.strftime('%Y-%m-%d')
                        })
                        
                        print(f"    ✓ [{date_obj.strftime('%Y-%m-%d')}] {title[:60]}...")
                        
                    except Exception as e:
                        continue
                
                # Anti-ban задержка
                time.sleep(1)
                
            except Exception as e:
                print(f"  ✗ Ошибка парсинга {feed_url}: {e}")
                continue
        
        print(f"  → Найдено в RSS: {len(results)} статей")
        return results
    
    def parse_html_sections(self, max_pages=5) -> List[Dict]:
        """Парсит HTML-страницы рубрик РБК"""
        print("\n[2/2] Парсинг HTML-страниц РБК...")
        results = []
        seen_urls = set()
        
        for section_url in self.HTML_SECTIONS:
            print(f"  Раздел: {section_url}")
            
            for page in range(1, max_pages + 1):
                try:
                    # Формируем URL с пагинацией
                    if page == 1:
                        url = section_url
                    else:
                        url = f"{section_url}?page={page}"
                    
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code != 200:
                        break
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Ищем блоки новостей
                    # РБК использует различные классы для новостных блоков
                    articles = soup.find_all(['a', 'div'], class_=re.compile(r'(item|card|news|article)', re.I))
                    
                    page_found = 0
                    for article in articles:
                        try:
                            # Ищем заголовок
                            title_elem = article.find(['span', 'div', 'h3', 'h2'], class_=re.compile(r'(title|headline)', re.I))
                            if not title_elem:
                                title_elem = article
                            
                            title = title_elem.get_text(strip=True)
                            
                            # Проверяем ключевые слова
                            if not self._contains_keyword(title):
                                continue
                            
                            # Ищем ссылку
                            link = None
                            if article.name == 'a':
                                link = article.get('href')
                            else:
                                link_elem = article.find('a')
                                if link_elem:
                                    link = link_elem.get('href')
                            
                            if not link:
                                continue
                            
                            # Нормализуем URL
                            if link.startswith('/'):
                                link = f"https://www.rbc.ru{link}"
                            elif not link.startswith('http'):
                                continue
                            
                            # Избегаем дубликатов
                            if link in seen_urls:
                                continue
                            seen_urls.add(link)
                            
                            # Пытаемся извлечь дату
                            date_elem = article.find(['time', 'span'], class_=re.compile(r'(date|time)', re.I))
                            date_str = datetime.now().strftime('%Y-%m-%d')
                            
                            if date_elem:
                                date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                                try:
                                    date_obj = self._parse_date(date_text)
                                    date_str = date_obj.strftime('%Y-%m-%d')
                                except:
                                    pass
                            
                            results.append({
                                'title': title,
                                'url': link,
                                'date': date_str
                            })
                            
                            page_found += 1
                            print(f"    ✓ [стр.{page}] {title[:60]}...")
                            
                        except Exception as e:
                            continue
                    
                    if page_found == 0:
                        break  # Переходим к следующему разделу
                    
                    # Anti-ban задержка
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"    ✗ Ошибка страницы {page}: {e}")
                    break
        
        print(f"  → Найдено в HTML: {len(results)} статей")
        return results
    
    def parse(self) -> List[Dict]:
        """Полный парсинг: RSS + HTML"""
        print("="*70)
        print("ПАРСЕР РБК - Поиск статей про Сбербанк за последние 60 дней")
        print("="*70)
        
        all_results = []
        seen_urls = set()
        
        # Парсим RSS
        rss_results = self.parse_rss_feeds()
        for item in rss_results:
            if item['url'] not in seen_urls:
                all_results.append(item)
                seen_urls.add(item['url'])
        
        # Парсим HTML (если RSS дал мало результатов)
        if len(all_results) < 10:
            print("\n⚠ RSS вернул мало статей, запускаем HTML-парсинг...")
            html_results = self.parse_html_sections(max_pages=3)
            for item in html_results:
                if item['url'] not in seen_urls:
                    all_results.append(item)
                    seen_urls.add(item['url'])
        
        print("\n" + "="*70)
        print(f"✅ ИТОГО найдено: {len(all_results)} статей про Сбербанк")
        print("="*70)
        
        return all_results


def main():
    """Тестовый запуск парсера"""
    parser = RBCParser()
    results = parser.parse()
    
    # Выводим результаты
    print("\nРезультаты:")
    for i, article in enumerate(results, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   URL: {article['url']}")
        print(f"   Дата: {article['date']}")


if __name__ == '__main__':
    main()
