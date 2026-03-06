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

API_KEY_NEWS = os.getenv("API_KEY_NEWS", "c09d91931a424c518822f9b4a997e4c5")
CHAT_ID = os.getenv("CHAT_ID", "-1002631457012")
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))

TZ = pytz.timezone("Asia/Jakarta")

sent_articles = set()

# =======================
# COMMAND /start
# =======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    message = (
        f"👋 Halo {user.first_name}!\n\n"
        f"🤖 Bot News XAUUSD aktif.\n\n"
        f"Bot ini akan mengirim berita penting tentang:\n"
        f"• Gold\n"
        f"• XAUUSD\n"
        f"• Ekonomi global\n\n"
        f"Channel tujuan berita:\n"
        f"{CHAT_ID}"
    )

    await update.message.reply_text(message)

# =======================
# AMBIL BERITA
# =======================

def get_news():

    try:

        url = (
            f"https://newsapi.org/v2/everything?"
            f"q=gold OR XAUUSD&"
            f"apiKey={API_KEY_NEWS}&"
            f"pageSize=5&"
            f"sortBy=publishedAt&"
            f"language=en"
        )

        response = requests.get(url, timeout=15)

        data = response.json()

        return data.get("articles", [])

    except Exception as e:

        print("⚠️ Gagal mengambil berita:", e)

        return []

# =======================
# ANALISA IMPACT
# =======================

def analyze_impact(title, description):

    impact_keywords = {

        "high": [
            "inflation",
            "interest rate",
            "federal reserve",
            "gold rally",
            "usd strengthens"
        ],

        "medium": [
            "gdp",
            "unemployment",
            "economic growth"
        ],

        "low": [
            "market update",
            "commodity",
            "dollar"
        ]

    }

    score = 0

    text = f"{title} {description}".lower()

    for level, keywords in impact_keywords.items():

        for kw in keywords:

            if kw in text:

                if level == "high":
                    score += 3

                elif level == "medium":
                    score += 2

                else:
                    score += 1

    percent = min(int(score / 10 * 100), 100)

    return percent

# =======================
# REKOMENDASI SIGNAL
# =======================

def recommend_action(percent):

    if percent >= 60:
        return "SELL"

    elif percent >= 30:
        return "BUY"

    else:
        return "HOLD"

# =======================
# KIRIM BERITA
# =======================

async def send_news(application):

    global sent_articles

    articles = get_news()

    if not articles:

        print("ℹ️ Tidak ada berita baru")

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

            title_id = title
            desc_id = desc

        action = recommend_action(percent)

        now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")

        message = (
            f"📰 *Berita Emas Terbaru*\n"
            f"🕒 {now} WIB\n\n"
            f"🗞️ *{title_id}*\n\n"
            f"{desc_id}\n\n"
            f"📊 Impact: *{percent}%*\n"
            f"📈 Rekomendasi: *{action}*\n\n"
            f"🔗 {url}"
        )

        try:

            await application.bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode="Markdown"
            )

            sent_articles.add(url)

            print("✅ Berita dikirim:", title[:50])

        except Exception as e:

            print("❌ Gagal kirim:", e)

        await asyncio.sleep(2)

# =======================
# LOOP BOT
# =======================

async def news_loop(application):

    print("🤖 Bot berita XAUUSD aktif")

    while True:

        try:

            await send_news(application)

        except Exception as e:

            print("⚠️ Error:", e)

        await asyncio.sleep(CHECK_INTERVAL)

# =======================
# MAIN
# =======================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    async def post_init(application):

        application.create_task(news_loop(application))

        print("🚀 Background news loop started")

    app.post_init = post_init

    print("✅ Bot Telegram berjalan")

    app.run_polling()

# =======================

if __name__ == "__main__":

    main()
