#!/bin/bash

echo "Starting Sberbank News System..."

echo "Step 1: Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Step 2: Parsing news..."
python parse_all.py

echo ""
echo "Step 3: Starting Flask server..."
echo "Flask will run on http://localhost:5000"
echo ""
echo "IMPORTANT: For Telegram Mini App to work, you need to:"
echo "1. Install ngrok: brew install ngrok (macOS) or download from ngrok.com"
echo "2. Run: ngrok http 5000"
echo "3. Copy the HTTPS URL from ngrok"
echo "4. Update WEB_APP_URL in .env file with ngrok URL"
echo "5. Restart the bot"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
