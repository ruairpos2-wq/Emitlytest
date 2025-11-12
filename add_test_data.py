from database import NewsDB
from datetime import datetime

db = NewsDB()

test_news = [
    {
        'title': 'Сбербанк увеличил чистую прибыль на 15% в третьем квартале',
        'content': 'Крупнейший российский банк отчитался о росте прибыли благодаря увеличению процентных доходов и активному развитию цифровых сервисов.',
        'date': '2025-11-12',
        'source': 'РБК',
        'url': 'https://www.rbc.ru/finances/12/11/2025/test1'
    },
    {
        'title': 'Сбербанк запустил новый сервис для малого бизнеса',
        'content': 'Банк представил платформу для автоматизации бухгалтерии и управления финансами малых предприятий.',
        'date': '2025-11-11',
        'source': 'РБК',
        'url': 'https://www.rbc.ru/business/11/11/2025/test2'
    },
    {
        'title': 'Акции Сбербанка выросли на 3% на фоне позитивной отчетности',
        'content': 'Инвесторы позитивно восприняли квартальные результаты банка, что привело к росту котировок.',
        'date': '2025-11-10',
        'source': 'Telegram @markettwits',
        'url': 'https://t.me/markettwits/12345'
    },
    {
        'title': 'Сбербанк инвестирует в развитие искусственного интеллекта',
        'content': 'Банк планирует направить значительные средства на развитие AI-технологий и машинного обучения.',
        'date': '2025-11-09',
        'source': 'РБК',
        'url': 'https://www.rbc.ru/technology/09/11/2025/test3'
    },
    {
        'title': 'Сбербанк снизил ставки по ипотеке для молодых семей',
        'content': 'Новая программа кредитования стартует с 15 ноября и предлагает льготные условия.',
        'date': '2025-11-08',
        'source': 'Telegram @markettwits',
        'url': 'https://t.me/markettwits/12340'
    }
]

print("Adding test news to database...")
for news in test_news:
    db.add_news(
        title=news['title'],
        content=news['content'],
        date=news['date'],
        source=news['source'],
        url=news['url']
    )
    print(f"Added: {news['title']}")

print(f"\nTotal news in database: {len(db.get_all_news())}")
print("Done! Refresh the browser to see the news.")
