import asyncio
import requests
import schedule
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext

# =========================
# CONFIG
# =========================
TELEGRAM_TOKEN = "8216938877:AAH7WKn9uJik5Hg3VJ2RIKuzTL7pqv6BIGY"
CHAT_ID = " -4881339106"

NEWS_API_URL = "https://www.forexfactory.com/calendar?json"

# =========================
# FUNCTION ANALISIS SENTIMEN
# =========================
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

# =========================
# FUNCTION AMBIL BERITA TERBARU
# =========================
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

# =========================
# BROADCAST KE GRUP
# =========================
async def broadcast_news(context: ContextTypes.DEFAULT_TYPE):
    messages = get_latest_news()
    for msg in messages:
        await context.bot.send_message(chat_id=CHAT_ID, text=msg)

# =========================
# COMMAND HANDLER
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Saya bot XAU/USD. Ketik /news untuk mendapatkan update berita terbaru emas."
    )

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = get_latest_news()
    for msg in messages:
        await update.message.reply_text(msg)

# =========================
# SCHEDULER OTOMATIS
# =========================
def schedule_broadcast(app):
    async def job():
        await broadcast_news(app)
    schedule.every(30).minutes.do(lambda: asyncio.create_task(job()))

# =========================
# MAIN BOT
# =========================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Handler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news))

    # Jalankan scheduler di background
    async def run_scheduler():
        while True:
            schedule.run_pending()
            await asyncio.sleep(10)

    # Run bot dan scheduler bersamaan
    async def main():
        asyncio.create_task(run_scheduler())
        await app.run_polling()

    asyncio.run(main())
