#!/usr/bin/env python3
"""
Главный скрипт для парсинга новостей про Сбербанк и инвестиции
Объединяет парсеры РБК (инвестиции и Сбербанк) и Telegram
"""

import json
import os
from datetime import datetime
from rbc_parser import RBCParser
from rbc_investments_parser import RBCInvestmentsParser
from telegram_selenium_parser import TelegramSeleniumParser


def save_results(data, filename):
    """Сохраняет результаты в JSON файл"""
    # Создаем папку results если её нет
    os.makedirs('results', exist_ok=True)
    
    filepath = os.path.join('results', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Файл сохранен: {filepath}")


def main():
    """Главная функция - запускает оба парсера"""
    print("\n" + "="*70)
    print("ПАРСИНГ НОВОСТЕЙ ПРО СБЕРБАНК")
    print("="*70)
    print(f"Дата запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # ========== ПАРСИНГ РБК ==========
    print("\n🔵 ША 1: ПАРСИНГ РБК")
    print("-"*70)
    
    try:
        rbc_parser = RBCParser()
        rbc_results = rbc_parser.parse()
        
        # Сохраняем результаты РБК
        save_results(rbc_results, 'rbc_results.json')
        
    except Exception as e:
        print(f"\n✗ Ошибка парсинга РБК: {e}")
        rbc_results = []
    
    # ========== ПАРСИНГ TELEGRAM ==========
    print("\n\n🔵 ШАГ 2: ПАРСИНГ TELEGRAM")
    print("-"*70)
    
    try:
        telegram_parser = TelegramSeleniumParser(headless=True)
        telegram_results = telegram_parser.parse_channel(
            channel_name='markettwits',
            target_messages=1000
        )
        
        # Сохраняем результаты Telegram
        save_results(telegram_results, 'telegram_results.json')
        
    except Exception as e:
        print(f"\n✗ Ошибка парсинга Telegram: {e}")
        import traceback
        traceback.print_exc()
        telegram_results = []
    
    # ========== ИТОГОВАЯ СТАТИСТИКА ==========
    print("\n\n" + "="*70)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("="*70)
    print(f"✅ Найдено {len(rbc_results)} статей на РБК")
    print(f"✅ Найдено {len(telegram_results)} постов в Telegram")
    print(f"📁 Файлы сохранены в ./results/")
    print("="*70)
    
    # Показываем примеры
    if rbc_results:
        print(f"\n📰 Примеры статей РБК (первые 3):")
        for i, article in enumerate(rbc_results[:3], 1):
            print(f"\n  {i}. {article['title']}")
            print(f"     Дата: {article['date']}")
            print(f"     URL: {article['url']}")
    
    if telegram_results:
        print(f"\n💬 Примеры постов Telegram (первые 3):")
        for i, post in enumerate(telegram_results[:3], 1):
            print(f"\n  {i}. [{post['date']}] {post['text'][:80]}...")
            print(f"     URL: {post['post_url']}")
    
    print("\n" + "="*70)
    print("✅ ПАРСИНГ ЗАВЕРШЕН")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
