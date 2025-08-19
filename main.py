import requests
from telegram import Bot

TELEGRAM_TOKEN = "8216938877:AAH7WKn9uJik5Hg3VJ2RIKuzTL7pqv6BIGY"
CHAT_ID = " -4881339106"

bot = Bot(token=TELEGRAM_TOKEN)
NEWS_API_URL = "https://www.forexfactory.com/calendar?json"

def analyze_sentiment(news_title):
    bullish_keywords = ["rise", "increase", "strong", "up", "gain"]
    bearish_keywords = ["fall", "drop", "weak", "down", "loss"]
    
    title_lower = news_title.lower()
    score = 0
    for word in bullish_keywords:
        if word in title_lower:
            score += 1
    for word in bearish_keywords:
        if word in title_lower:
            score -= 1

    if score > 0:
        return "BUY", min(score*20, 100)
    elif score < 0:
        return "SELL", min(abs(score)*20, 100)
    else:
        return "HOLD", 0

def get_latest_news():
    try:
        response = requests.get(NEWS_API_URL)
        data = response.json()
        news_list = data.get("events", [])[:5]
        xau_news = [n for n in news_list if "gold" in n.get("currency", "").lower() or "xau" in n.get("currency", "").lower()]
        messages = []
        for news in xau_news:
            title = news.get("title", "No title")
            impact = news.get("impact", "Medium")
            recommendation, perc = analyze_sentiment(title)
            msg = f"📰 {title}\nImpact: {impact}\nRecommendation: {recommendation} ({perc}%)"
            messages.append(msg)
        return messages if messages else ["Tidak ada berita XAU/USD terbaru."]
    except Exception as e:
        return [f"Error ambil news: {e}"]

# Kirim berita ke grup
messages = get_latest_news()
for msg in messages:
    bot.send_message(chat_id=CHAT_ID, text=msg)
