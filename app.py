from flask import Flask, render_template, jsonify
from database import NewsDB
import config

app = Flask(__name__)
db = NewsDB()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/news')
def get_news():
    news = db.get_all_news()
    return jsonify(news)

if __name__ == '__main__':
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=True)
