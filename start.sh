#!/bin/bash#!/bin/bash

# Скрипт для быстрого запуска всей системы

echo "Starting Sberbank News System..."

echo "🚀 ЗАПУСК НОВОСТНОГО АГРЕГАТОРА"

echo "================================"echo "Step 1: Installing dependencies..."

echo ""pip install -r requirements.txt



# 1. Парсинг и импортecho ""

echo "📊 Шаг 1/2: Парсинг новостей..."echo "Step 2: Parsing news..."

python3 run_full_parsing.pypython parse_all.py



echo ""echo ""

echo "================================"echo "Step 3: Starting Flask server..."

echo ""echo "Flask will run on http://localhost:5000"

echo ""

# 2. Запуск веб-сервераecho "IMPORTANT: For Telegram Mini App to work, you need to:"

echo "🌐 Шаг 2/2: Запуск веб-интерфейса..."echo "1. Install ngrok: brew install ngrok (macOS) or download from ngrok.com"

echo "Откройте браузер: http://127.0.0.1:5001"echo "2. Run: ngrok http 5000"

echo ""echo "3. Copy the HTTPS URL from ngrok"

python3 app.pyecho "4. Update WEB_APP_URL in .env file with ngrok URL"

echo "5. Restart the bot"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
