import asyncio
import requests
from telegram import Bot

# --- CONFIG ---
API_KEY_NEWS = "c09d91931a424c518822f9b4a997e4c5"
CHAT_ID = "-1002510797113"
BOT_TOKEN = "8216938877:AAH7WKn9uJik5Hg3VJ2RIKuzTL7pqv6BIGY"

bot = Bot(token=BOT_TOKEN)

# Fungsi ambil berita terbaru
def get_news():
    url = f"https://newsapi.org/v2/everything?q=gold OR XAUUSD&apiKey={API_KEY_NEWS}&pageSize=5"
    response = requests.get(url)
    data = response.json()
    return data.get("articles", [])

# Analisis dampak berita ke XAU/USD
def analyze_impact(title, description):
    impact_keywords = {
        "high": ["inflation", "interest rate", "federal reserve", "gold rally"],
        "medium": ["GDP", "unemployment", "economic growth"],
        "low": ["general news", "market update"]
    }
    score = 0
    text = f"{title} {description}".lower()
    for level, keywords in impact_keywords.items():
        for kw in keywords:
            if kw.lower() in text:
                if level == "high": score += 3
                elif level == "medium": score += 2
                else: score += 1
    # Hitung persentase impact (maks 10)
    percent = min(int(score / 10 * 100), 100)
    return percent

# Tentukan rekomendasi buy/sell
def recommend_action(percent):
    if percent >= 60:
        return "SELL"
    elif percent >= 30:
        return "BUY"
    else:
        return "HOLD"

# Kirim berita ke Telegram
async def send_news():
    articles = get_news()
    for article in articles:
        title = article.get("title", "")
        desc = article.get("description", "")
        percent = analyze_impact(title, desc)
        action = recommend_action(percent)
        text = f"{title}\n{desc}\nImpact: {percent}%\nRecommendation: {action}"
        await bot.send_message(chat_id=CHAT_ID, text=text)
        await asyncio.sleep(1)  # delay supaya tidak spam

# Main
async def main():
    while True:
        await send_news()
        await asyncio.sleep(3600)  # cek setiap 1 jam

if __name__ == "__main__":
    asyncio.run(main())
