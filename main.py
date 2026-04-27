#!/usr/bin/env python3

import os
import asyncio
import requests
from datetime import datetime
import pytz

from deep_translator import GoogleTranslator

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

# =======================
# CONFIG
# =======================

API_KEY_NEWS = os.getenv("API_KEY_NEWS", "YOUR_NEWS_API_KEY")
CHAT_ID = os.getenv("CHAT_ID", "-1002631457012")
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))

TZ = pytz.timezone("Asia/Jakarta")

sent_articles = set()

# =======================
# START COMMAND
# =======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    await update.message.reply_text(
        f"👋 Halo {user.first_name}!\n\n"
        "🤖 Bot News XAUUSD aktif\n\n"
        "📊 Mengirim berita ekonomi & gold secara otomatis\n"
        "📡 Mode: REALTIME NEWS SCANNER"
    )

# =======================
# GET NEWS
# =======================

def get_news():

    try:
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q=gold OR XAUUSD OR inflation OR federal reserve&"
            f"apiKey={API_KEY_NEWS}&"
            f"pageSize=5&"
            f"sortBy=publishedAt&"
            f"language=en"
        )

        response = requests.get(url, timeout=15)
        data = response.json()

        return data.get("articles", [])

    except Exception as e:
        print("⚠️ Error news:", e)
        return []

# =======================
# ANALISA IMPACT
# =======================

def analyze_impact(title, description):

    text = f"{title} {description}".lower()

    high = ["inflation", "interest rate", "federal reserve", "crisis", "war"]
    medium = ["gdp", "unemployment", "economic"]
    low = ["market", "commodity", "dollar"]

    score = 0

    for w in high:
        if w in text:
            score += 3

    for w in medium:
        if w in text:
            score += 2

    for w in low:
        if w in text:
            score += 1

    return min(int(score / 10 * 100), 100)

# =======================
# RECOMMENDATION
# =======================

def recommend_action(percent):

    if percent >= 60:
        return "SELL"

    elif percent >= 30:
        return "BUY"

    return "HOLD"

# =======================
# SEND NEWS
# =======================

async def send_news(app):

    global sent_articles

    articles = get_news()

    if not articles:
        return

    for a in articles:

        url = a.get("url", "")
        title = a.get("title", "")
        desc = a.get("description", "")

        if not url or url in sent_articles:
            continue

        impact = analyze_impact(title, desc)

        if impact == 0:
            continue

        # translate
        try:
            title_id = GoogleTranslator(source="auto", target="id").translate(title or "")
            desc_id = GoogleTranslator(source="auto", target="id").translate(desc or "")
        except:
            title_id = title
            desc_id = desc

        action = recommend_action(impact)

        now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")

        message = (
            f"📰 *XAUUSD NEWS UPDATE*\n"
            f"🕒 {now} WIB\n\n"
            f"📌 *{title_id}*\n\n"
            f"{desc_id}\n\n"
            f"📊 Impact Score: {impact}%\n"
            f"📈 Signal Bias: {action}\n\n"
            f"🔗 Source: {url}"
        )

        try:
            await app.bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode="Markdown"
            )

            sent_articles.add(url)

            print("✅ Sent:", title[:50])

        except Exception as e:
            print("❌ Send error:", e)

        await asyncio.sleep(2)

# =======================
# LOOP
# =======================

async def news_loop(app):

    print("🚀 News system started")

    while True:
        try:
            await send_news(app)
        except Exception as e:
            print("⚠️ Loop error:", e)

        await asyncio.sleep(CHECK_INTERVAL)

# =======================
# POST INIT (FIXED)
# =======================

async def post_init(app):

    loop = asyncio.get_running_loop()
    loop.create_task(news_loop(app))

    print("✅ Background task running safely")

# =======================
# MAIN
# =======================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.post_init = post_init

    print("🤖 Bot running...")
    app.run_polling(drop_pending_updates=True)

# =======================

if __name__ == "__main__":
    main()
