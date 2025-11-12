import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID', 'YOUR_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH', 'YOUR_API_HASH')
WEB_APP_URL = os.getenv('WEB_APP_URL', 'http://localhost:5000')
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
