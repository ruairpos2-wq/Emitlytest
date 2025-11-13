#!/usr/bin/env python3
"""
Скрипт для импорта результатов парсинга в базу данных
Загружает новости про Сбербанк и общие инвестиционные новости
"""

import json
from database import NewsDB


def import_from_json():
    """Импортирует результаты из JSON файлов в базу данных"""
    db = NewsDB()
    
    print("="*70)
    print("ИМПОРТ РЕЗУЛЬТАТОВ ПАРСИНГА В БАЗУ ДАННЫХ")
    print("="*70)
    
    # Импорт из Telegram
    print("\n📱 Импорт постов из Telegram...")
    try:
        with open('results/telegram_results.json', 'r', encoding='utf-8') as f:
            telegram_news = json.load(f)
        
        telegram_count = 0
        for news in telegram_news:
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
                print(f"  ✓ {title[:60]}...")
        
        print(f"\n✅ Импортировано из Telegram: {telegram_count} постов")
        
    except FileNotFoundError:
        print("⚠ Файл telegram_results.json не найден")
    except Exception as e:
        print(f"✗ Ошибка импорта Telegram: {e}")
    
    # Импорт из РБК (Сбербанк)
    print("\n📰 Импорт статей про Сбербанк из РБК...")
    try:
        with open('results/rbc_results.json', 'r', encoding='utf-8') as f:
            rbc_news = json.load(f)
        
        rbc_sber_count = 0
        for news in rbc_news:
            success = db.add_news(
                title=news['title'],
                content=news['title'],  # У РБК только заголовок
                date=news['date'] + ' 00:00:00',
                source='РБК',
                url=news['url'],
                category='sberbank'
            )
            
            if success:
                rbc_sber_count += 1
                print(f"  ✓ {news['title'][:60]}...")
        
        print(f"\n✅ Импортировано статей про Сбербанк: {rbc_sber_count}")
        
    except FileNotFoundError:
        print("⚠ Файл rbc_results.json не найден")
        rbc_sber_count = 0
    except Exception as e:
        print(f"✗ Ошибка импорта РБК (Сбербанк): {e}")
        rbc_sber_count = 0
    
    # Импорт инвестиционных новостей из РБК
    print("\n📊 Импорт инвестиционных новостей из РБК...")
    try:
        with open('results/rbc_investments_results.json', 'r', encoding='utf-8') as f:
            rbc_inv_news = json.load(f)
        
        rbc_inv_count = 0
        for news in rbc_inv_news:
            success = db.add_news(
                title=news['title'],
                content=news['title'],
                date=news['date'] + ' 00:00:00',
                source='РБК Инвестиции',
                url=news['url'],
                category='general'  # Общая категория для инвестиций
            )
            
            if success:
                rbc_inv_count += 1
                print(f"  ✓ {news['title'][:60]}...")
        
        print(f"\n✅ Импортировано инвестиционных новостей: {rbc_inv_count}")
        
    except FileNotFoundError:
        print("⚠ Файл rbc_investments_results.json не найден")
        rbc_inv_count = 0
    except Exception as e:
        print(f"✗ Ошибка импорта РБК (инвестиции): {e}")
        rbc_inv_count = 0
    
    # Итоговая статистика
    print("\n" + "="*70)
    print("📊 СТАТИСТИКА БАЗЫ ДАННЫХ")
    print("="*70)
    
    all_news = db.get_all_news()
    sber_news = db.get_all_news(category='sberbank')
    
    print(f"Всего новостей: {len(all_news)}")
    print(f"Новостей про Сбербанк: {len(sber_news)}")
    print(f"Общих новостей: {len(all_news) - len(sber_news)}")
    
    print("\n" + "="*70)
    print("✅ ИМПОРТ ЗАВЕРШЕН")
    print("="*70)


if __name__ == '__main__':
    import_from_json()
