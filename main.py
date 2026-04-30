#!/usr/bin/env python3

import os
import asyncio
import requests
from datetime import datetime, timedelta
import pytz

from deep_translator import GoogleTranslator

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

# =======================
# ENV
# =======================

API_KEY_NEWS = os.getenv("API_KEY_NEWS")
CHAT_ID = os.getenv("CHAT_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
THREAD_ID = os.getenv("THREAD_ID")

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))

if not API_KEY_NEWS or not CHAT_ID or not BOT_TOKEN:
    raise ValueError("Missing ENV")

CHAT_ID = int(CHAT_ID)
THREAD_ID = int(THREAD_ID) if THREAD_ID else None

TZ = pytz.timezone("Asia/Jakarta")

sent_articles = set()

# 🔥 NEW: global cooldown
last_sent_time = None
COOLDOWN = timedelta(hours=1)

# =======================
# START
# =======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot News XAUUSD aktif\n"
        "⏱ Kirim berita setiap 1 jam sekali"
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

        r = requests.get(url, timeout=15)
        return r.json().get("articles", [])

    except Exception as e:
        print("News error:", e)
        return []

# =======================
# ANALYSIS
# =======================

def analyze_impact(title, description):

    text = f"{title} {description}".lower()

    high = ["inflation", "interest rate", "federal reserve", "war", "crisis"]
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
# SIGNAL
# =======================

def recommend_action(score):
    if score >= 60:
        return "SELL"
    elif score >= 30:
        return "BUY"
    return "HOLD"

# =======================
# SEND MESSAGE
# =======================

async def send_message(app, text):

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    if THREAD_ID:
        payload["message_thread_id"] = THREAD_ID

    await app.bot.send_message(**payload)

# =======================
# NEWS SENDER (FIXED COOLDOWN)
# =======================

async def send_news(app):

    global sent_articles, last_sent_time

    now = datetime.now(TZ)

    # 🔥 BLOCK: 1 jam rule
    if last_sent_time and (now - last_sent_time) < COOLDOWN:
        print("⏳ Cooldown active, skip send")
        return

    articles = get_news()

    sent_any = False

    for a in articles:

        url = a.get("url")
        title = a.get("title", "")
        desc = a.get("description", "")

        if not url or url in sent_articles:
            continue

        impact = analyze_impact(title, desc)
        if impact == 0:
            continue

        try:
            title_id = GoogleTranslator(source="auto", target="id").translate(title or "")
            desc_id = GoogleTranslator(source="auto", target="id").translate(desc or "")
        except:
            title_id = title
            desc_id = desc

        action = recommend_action(impact)

        now_str = now.strftime("%Y-%m-%d %H:%M:%S")

        message = (
            f"📰 *XAUUSD NEWS UPDATE*\n"
            f"🕒 {now_str} WIB\n\n"
            f"📌 *{title_id}*\n\n"
            f"{desc_id}\n\n"
            f"📊 Impact: {impact}%\n"
            f"📈 Bias: {action}\n\n"
            f"🔗 {url}"
        )

        try:
            await send_message(app, message)
            sent_articles.add(url)
            sent_any = True
            print("Sent:", title[:40])

        except Exception as e:
            print("Send error:", e)

        await asyncio.sleep(2)

    # 🔥 update cooldown only if sent
    if sent_any:
        last_sent_time = now

# =======================
# LOOP
# =======================

async def news_loop(app):

    print("🚀 News bot running...")

    while True:
        await send_news(app)
        await asyncio.sleep(CHECK_INTERVAL)

# =======================
# INIT
# =======================

async def post_init(app):
    asyncio.create_task(news_loop(app))
    print("✅ Background task started")

# =======================
# MAIN
# =======================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.post_init = post_init

    print("🤖 Bot Running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
