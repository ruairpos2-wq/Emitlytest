from flask import Flask, render_template, jsonify
from database import NewsDB

app = Flask(__name__)
db = NewsDB()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/news/recent')
def get_recent_news():
    """
    Все свежие новости из РБК (инвестиции) и Telegram
    Максимум 20 штук по свежести
    """
    all_news = db.get_all_news()
    # Сортируем по дате (самые свежие первыми)
    sorted_news = sorted(all_news, key=lambda x: x['date'], reverse=True)
    return jsonify(sorted_news[:20])

@app.route('/api/news/sberbank')
def get_sberbank_news():
    """
    Новости про Сбербанк из РБК и Telegram
    Максимум 5 из РБК + максимум 5 из Telegram
    """
    sber_news = db.get_all_news(category='sberbank')
    
    # Разделяем по источникам
    rbc_news = [n for n in sber_news if 'РБК' in n['source']]
    telegram_news = [n for n in sber_news if 'Telegram' in n['source']]
    
    # Берем максимум 5 из каждого источника (самые свежие)
    rbc_sorted = sorted(rbc_news, key=lambda x: x['date'], reverse=True)[:5]
    telegram_sorted = sorted(telegram_news, key=lambda x: x['date'], reverse=True)[:5]
    
    # Объединяем и сортируем по дате
    combined = rbc_sorted + telegram_sorted
    result = sorted(combined, key=lambda x: x['date'], reverse=True)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
