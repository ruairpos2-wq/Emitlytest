#!/usr/bin/env python3
# Полный цикл парсинга новостей

import json
import os
from datetime import datetime
from rbc_parser import RBCParser
from rbc_investments_parser import RBCInvestmentsParser
from telegram_selenium_parser import TelegramSeleniumParser
from database import NewsDB


def save_results(data, filename):
    """Сохраняет результаты в JSON файл"""
    os.makedirs('results', exist_ok=True)
    filepath = os.path.join('results', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Файл сохранен: {filepath}")


def import_to_db(telegram_results, rbc_sber_results, rbc_inv_results):
    """Импортирует результаты в базу данных"""
    db = NewsDB()
    
    print("\n" + "="*70)
    print("ИМПОРТ В БАЗУ ДАННЫХ")
    print("="*70)
    
    # Импорт Telegram (Сбербанк)
    print("\n📱 Импорт Telegram (Сбербанк)...")
    telegram_count = 0
    for news in telegram_results:
        title = news['text'][:100] + '...' if len(news['text']) > 100 else news['text']
        success = db.add_news(
            title=title,
            content=news['text'],
            date=news['date'] + ' 00:00:00',
            source='Telegram @markettwits',
            url=news['post_url'],
            category='sberbank'
        )
        if success:
            telegram_count += 1
    print(f"✅ {telegram_count} постов")
    
    # Импорт РБК (Сбербанк)
    print("\n📰 Импорт РБК (Сбербанк)...")
    rbc_sber_count = 0
    for news in rbc_sber_results:
        success = db.add_news(
            title=news['title'],
            content=news['title'],
            date=news['date'] + ' 00:00:00',
            source='РБК',
            url=news['url'],
            category='sberbank'
        )
        if success:
            rbc_sber_count += 1
    print(f"✅ {rbc_sber_count} статей")
    
    # Импорт РБК (инвестиции)
    print("\n📊 Импорт РБК (инвестиции)...")
    rbc_inv_count = 0
    for news in rbc_inv_results:
        success = db.add_news(
            title=news['title'],
            content=news['title'],
            date=news['date'] + ' 00:00:00',
            source='РБК Инвестиции',
            url=news['url'],
            category='general'
        )
        if success:
            rbc_inv_count += 1
    print(f"✅ {rbc_inv_count} статей")
    
    print("\n" + "="*70)
    print(f"📊 ИТОГО В БАЗЕ:")
    all_news = db.get_all_news()
    sber_news = db.get_all_news(category='sberbank')
    print(f"  Всего новостей: {len(all_news)}")
    print(f"  Про Сбербанк: {len(sber_news)}")
    print(f"  Общих (инвестиции): {len(all_news) - len(sber_news)}")
    print("="*70)


def main():
    """Главная функция"""
    print("\n" + "="*70)
    print("🚀 ПОЛНЫЙ ЦИКЛ ПАРСИНГА И ИМПОРТА НОВОСТЕЙ")
    print("="*70)
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # ========== 1. РБК ИНВЕСТИЦИИ ==========
    print("\n\n🔵 ШАГ 1/3: ПАРСИНГ РБК (ИНВЕСТИЦИИ)")
    print("-"*70)
    
    try:
        rbc_inv_parser = RBCInvestmentsParser()
        rbc_inv_results = rbc_inv_parser.parse()
        save_results(rbc_inv_results, 'rbc_investments_results.json')
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        rbc_inv_results = []
    
    # ========== 2. РБК СБЕРБАНК ==========
    print("\n\n🔵 ШАГ 2/3: ПАРСИНГ РБК (СБЕРБАНК)")
    print("-"*70)
    
    try:
        rbc_sber_parser = RBCParser()
        rbc_sber_results = rbc_sber_parser.parse()
        save_results(rbc_sber_results, 'rbc_results.json')
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        rbc_sber_results = []
    
    # ========== 3. TELEGRAM ==========
    print("\n\n🔵 ШАГ 3/3: ПАРСИНГ TELEGRAM")
    print("-"*70)
    
    try:
        telegram_parser = TelegramSeleniumParser(headless=True)
        telegram_results = telegram_parser.parse_channel(
            channel_name='markettwits',
            target_messages=1000
        )
        save_results(telegram_results, 'telegram_results.json')
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        telegram_results = []
    
    # ========== 4. ИМПОРТ В БД ==========
    import_to_db(telegram_results, rbc_sber_results, rbc_inv_results)
    
    # ========== ИТОГОВАЯ СТАТИСТИКА ==========
    print("\n\n" + "="*70)
    print("✅ ПАРСИНГ ЗАВЕРШЕН")
    print("="*70)
    print(f"📊 РБК (инвестиции): {len(rbc_inv_results)} статей")
    print(f"📰 РБК (Сбербанк): {len(rbc_sber_results)} статей")
    print(f"💬 Telegram: {len(telegram_results)} постов")
    print("="*70)
    print("🌐 Запустите Flask: python3 app.py")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
