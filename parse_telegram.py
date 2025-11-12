from telethon.sync import TelegramClient
from datetime import datetime
from database import NewsDB
import config

class TelegramParser:
    def __init__(self):
        self.api_id = config.TELEGRAM_API_ID
        self.api_hash = config.TELEGRAM_API_HASH
        self.client = None
    
    def parse_channel(self, channel_username='markettwits', keyword='Сбербанк', limit=5):
        results = []
        try:
            with TelegramClient('session_name', self.api_id, self.api_hash) as client:
                messages = client.get_messages(channel_username, limit=100)
                
                count = 0
                for message in messages:
                    if count >= limit:
                        break
                    
                    if message.text and keyword in message.text:
                        date_str = message.date.strftime('%Y-%m-%d %H:%M:%S') if message.date else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        results.append({
                            'title': message.text[:100] + '...' if len(message.text) > 100 else message.text,
                            'content': message.text,
                            'date': date_str,
                            'source': 'Telegram @markettwits',
                            'url': f'https://t.me/{channel_username}/{message.id}'
                        })
                        count += 1
                        
        except Exception as e:
            print(f"Error fetching Telegram messages: {e}")
        
        return results

def main():
    parser = TelegramParser()
    db = NewsDB()
    
    news_list = parser.parse_channel()
    print(f"Found {len(news_list)} messages from Telegram")
    
    for news in news_list:
        db.add_news(
            title=news['title'],
            content=news['content'],
            date=news['date'],
            source=news['source'],
            url=news['url']
        )
    
    print("Telegram messages saved to database")

if __name__ == '__main__':
    main()
