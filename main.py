#!/usr/bin/env python3
import os
import asyncio
import requests
from telegram import Bot
from deep_translator import GoogleTranslator
from datetime import datetime
import pytz

# =======================
# CONFIG
# =======================
API_KEY_NEWS = os.getenv("API_KEY_NEWS", "c09d91931a424c518822f9b4a997e4c5")
CHAT_ID = os.getenv("CHAT_ID", "-1002631457012")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8216938877:AAH7WKn9uJik5Hg3VJ2RIKuzTL7pqv6BIGY")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))  # detik
TZ = pytz.timezone("Asia/Jakarta")

bot = Bot(token=BOT_TOKEN)
sent_articles = set()

# =======================
# Ambil berita terbaru
# =======================
def get_news():
    try:
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q=gold OR XAUUSD&apiKey={API_KEY_NEWS}&pageSize=5&sortBy=publishedAt&language=en"
        )
        response = requests.get(url, timeout=15)
        data = response.json()
        return data.get("articles", [])
    except Exception as e:
        print("⚠️ Gagal mengambil berita:", e)
        return []

# =======================
# Analisis dampak berita
# =======================
def analyze_impact(title, description):
    impact_keywords = {
        "high": ["inflation", "interest rate", "federal reserve", "gold rally", "usd strengthens"],
        "medium": ["GDP", "unemployment", "economic growth"],
        "low": ["market update", "commodity", "dollar"]
    }

    score = 0
    text = f"{title} {description}".lower()

    for level, keywords in impact_keywords.items():
        for kw in keywords:
            if kw in text:
                score += {"high": 3, "medium": 2, "low": 1}[level]

    percent = min(int(score / 10 * 100), 100)
    return percent

# =======================
# Rekomendasi buy/sell
# =======================
def recommend_action(percent):
    if percent >= 60:
        return "SELL"
    elif percent >= 30:
        return "BUY"
    else:
        return "HOLD"

# =======================
# Kirim berita ke Telegram
# =======================
async def send_news():
    global sent_articles
    articles = get_news()

    if not articles:
        print("ℹ️ Tidak ada berita baru ditemukan.")
        return

    for article in articles:
        url = article.get("url", "")
        title = article.get("title", "")
        desc = article.get("description", "")

        if not url or url in sent_articles:
            continue

        percent = analyze_impact(title, desc)
        if percent == 0:
            continue

        try:
            title_id = GoogleTranslator(source="auto", target="id").translate(title or "")
            desc_id = GoogleTranslator(source="auto", target="id").translate(desc or "")
        except Exception:
            title_id, desc_id = title, desc

        action = recommend_action(percent)
        now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")

        message = (
            f"📰 *Berita Emas Terbaru ({now})*\n\n"
            f"🗞️ *{title_id}*\n"
            f"{desc_id}\n\n"
            f"📊 Impact: {percent}%\n"
            f"📈 Rekomendasi: {action}\n"
            f"🔗 Sumber: {url}"
        )

        try:
            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
            sent_articles.add(url)
            print(f"✅ Dikirim: {title[:60]}...")
        except Exception as e:
            print("❌ Gagal kirim Telegram:", e)

        await asyncio.sleep(2)

# =======================
# Loop utama
# =======================
async def main():
    print("🤖 Bot berita XAU/USD aktif dan berjalan...")
    while True:
        try:
            await send_news()
        except Exception as e:
            print("⚠️ Error utama:", e)
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
