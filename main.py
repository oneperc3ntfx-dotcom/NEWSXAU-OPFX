import asyncio
import aiohttp
from textblob import TextBlob
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ===== Konfigurasi =====
TELEGRAM_TOKEN = "8216938877:AAH7WKn9uJik5Hg3VJ2RIKuzTL7pqv6BIGY"
CHAT_ID =  -4881339106  # ganti dengan chat_id grup atau channel
NEWS_API_KEY = "c09d91931a424c518822f9b4a997e4c5"
SYMBOL = "XAUUSD"
CHECK_INTERVAL = 600  # detik

# ===== Analisis sentimen =====
def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "BUY"
    elif polarity < -0.1:
        return "SELL"
    else:
        return "NEUTRAL"

# ===== Ambil berita =====
async def fetch_news():
    url = f"https://newsapi.org/v2/everything?q={SYMBOL}&sortBy=publishedAt&apiKey={NEWS_API_KEY}&language=en&pageSize=5"
    news_list = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                for article in data.get("articles", []):
                    title = article["title"]
                    link = article["url"]
                    recommendation = analyze_sentiment(title)
                    news_list.append(f"{title}\nRekomendasi: {recommendation}\n{link}")
    except Exception as e:
        print("Error ambil news:", e)
    return news_list

# ===== Kirim berita =====
async def broadcast_news(app):
    while True:
        news_items = await fetch_news()
        if news_items:
            for news in news_items:
                await app.bot.send_message(chat_id=CHAT_ID, text=news)
        else:
            await app.bot.send_message(chat_id=CHAT_ID, text="Tidak ada berita baru.")
        await asyncio.sleep(CHECK_INTERVAL)

# ===== /start handler =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot aktif! Akan mengirim berita forex beserta rekomendasi buy/sell.")

# ===== Main =====
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # jalankan loop broadcast di background
    asyncio.create_task(broadcast_news(app))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
