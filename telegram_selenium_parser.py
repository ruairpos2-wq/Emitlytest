#!/usr/bin/env python3
# Парсер Telegram через Selenium

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from datetime import datetime
from typing import List, Dict
import re


class TelegramSeleniumParser:
    """Парсер Telegram через Selenium с автопрокруткой"""
    
    KEYWORDS = ['сбербанк', 'сбер', 'sberbank', 'sber']
    
    def __init__(self, headless=True):
        """
        Args:
            headless: Запускать браузер в фоновом режиме (без GUI)
        """
        self.headless = headless
        self.driver = None
        
    def _setup_driver(self):
        """Настраивает Chrome WebDriver"""
        print("Настройка Chrome WebDriver...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        # Для macOS: используем встроенный Chrome
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✓ WebDriver инициализирован")
        except Exception as e:
            print(f"✗ Ошибка инициализации WebDriver: {e}")
            print("\nУстановите ChromeDriver:")
            print("  brew install chromedriver")
            print("  brew install --cask google-chrome")
            raise
    
    def _scroll_to_load_messages(self, channel_url: str, target_messages=200):
        """Прокручивает страницу для загрузки большего количества сообщений"""
        print(f"\nЗагружаю {channel_url}...")
        self.driver.get(channel_url)
        
        # Ждем загрузки первых сообщений
        time.sleep(3)
        
        print(f"Цель: загрузить {target_messages} сообщений через прокрутку...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        messages_count = 0
        scroll_attempts = 0
        max_scrolls = 50  # Максимум прокруток
        
        while messages_count < target_messages and scroll_attempts < max_scrolls:
            # Прокручиваем вверх (к более старым сообщениям)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # Считаем текущее количество сообщений
            messages = self.driver.find_elements(By.CLASS_NAME, 'tgme_widget_message')
            messages_count = len(messages)
            
            scroll_attempts += 1
            
            print(f"  [Прокрутка {scroll_attempts}] Загружено сообщений: {messages_count}/{target_messages}")
            
            # Проверяем, появились ли новые сообщения
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height and messages_count > 20:
                print("  Достигнут конец канала")
                break
            last_height = new_height
            
            # Если достигли цели - останавливаемся
            if messages_count >= target_messages:
                print(f"  ✓ Цель достигнута: {messages_count} сообщений")
                break
        
        print(f"\n→ Итого загружено: {messages_count} сообщений")
        return messages_count
    
    def _contains_keyword(self, text: str) -> bool:
        """Проверяет наличие ключевых слов"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.KEYWORDS)
    
    def parse_channel(self, channel_name: str, target_messages=1000) -> List[Dict]:
        """
        Парсит публичный Telegram-канал
        
        Args:
            channel_name: Имя канала без @ (например, 'markettwits')
            target_messages: Целевое количество сообщений для загрузки
            
        Returns:
            List[Dict]: Список постов с упоминанием Сбербанка
        """
        print("="*70)
        print(f"ПАРСЕР TELEGRAM @{channel_name} - Поиск упоминаний Сбербанка")
        print("="*70)
        
        results = []
        seen_urls = set()
        
        try:
            # Инициализируем WebDriver
            self._setup_driver()
            
            # Формируем URL публичного просмотра
            channel_url = f"https://t.me/s/{channel_name}"
            
            # Прокручиваем для загрузки сообщений
            total_messages = self._scroll_to_load_messages(channel_url, target_messages)
            
            # Получаем HTML-код страницы
            print("\nИзвлекаю данные из загруженных сообщений...")
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Находим все сообщения
            messages = soup.find_all('div', class_='tgme_widget_message')
            print(f"Найдено сообщений в HTML: {len(messages)}")
            
            # Обрабатываем каждое сообщение
            for message in messages:
                try:
                    # Извлекаем текст
                    text_div = message.find('div', class_='tgme_widget_message_text')
                    if not text_div:
                        continue
                    
                    text = text_div.get_text(strip=True)
                    
                    # Фильтруем по ключевым словам
                    if not self._contains_keyword(text):
                        continue
                    
                    # Извлекаем дату
                    date_elem = message.find('time')
                    date_str = None
                    if date_elem:
                        date_str = date_elem.get('datetime')
                        if date_str:
                            try:
                                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                date_str = date_obj.strftime('%Y-%m-%d')
                            except:
                                date_str = datetime.now().strftime('%Y-%m-%d')
                    else:
                        date_str = datetime.now().strftime('%Y-%m-%d')
                    
                    # Извлекаем ссылку на пост
                    link_elem = message.find('a', class_='tgme_widget_message_date')
                    post_url = link_elem.get('href') if link_elem else f"https://t.me/{channel_name}"
                    
                    # Проверяем дубликаты
                    if post_url in seen_urls:
                        continue
                    seen_urls.add(post_url)
                    
                    # Извлекаем ID поста
                    post_id = ''
                    if link_elem:
                        href = link_elem.get('href', '')
                        match = re.search(r'/(\d+)$', href)
                        if match:
                            post_id = match.group(1)
                    
                    results.append({
                        'text': text[:200] + '...' if len(text) > 200 else text,
                        'date': date_str,
                        'post_url': post_url
                    })
                    
                    print(f"  ✓ [ID {post_id}] [{date_str}] {text[:60]}...")
                    
                except Exception as e:
                    continue
            
            print("\n" + "="*70)
            print(f"✅ Найдено постов с упоминанием Сбербанка: {len(results)}")
            print("="*70)
            
        except Exception as e:
            print(f"\n✗ Ошибка парсинга: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Закрываем браузер
            if self.driver:
                self.driver.quit()
                print("\n✓ WebDriver закрыт")
        
        return results


def main():
    """Тестовый запуск парсера"""
    parser = TelegramSeleniumParser(headless=False)  # headless=False для отладки
    results = parser.parse_channel('markettwits', target_messages=1000)
    
    # Выводим результаты
    print("\nРезультаты:")
    for i, post in enumerate(results, 1):
        print(f"\n{i}. [{post['date']}] {post['text'][:80]}...")
        print(f"   URL: {post['post_url']}")


if __name__ == '__main__':
    main()
