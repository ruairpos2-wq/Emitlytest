import sqlite3
from datetime import datetime

class NewsDB:
    def __init__(self, db_path='news.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                date TEXT NOT NULL,
                source TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                category TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_news(self, title, content, date, source, url, category='general'):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO news (title, content, date, source, url, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, content, date, source, url, category))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding news: {e}")
            return False
    
    def get_all_news(self, category=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if category:
            cursor.execute('SELECT title, content, date, source, url, category FROM news WHERE category = ? ORDER BY date DESC', (category,))
        else:
            cursor.execute('SELECT title, content, date, source, url, category FROM news ORDER BY date DESC')
        rows = cursor.fetchall()
        conn.close()
        return [{'title': r[0], 'content': r[1], 'date': r[2], 'source': r[3], 'url': r[4], 'category': r[5]} for r in rows]
    
    def clear_news(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM news')
        conn.commit()
        conn.close()
