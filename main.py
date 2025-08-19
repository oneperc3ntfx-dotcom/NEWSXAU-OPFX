import asyncio
import aiohttp
from textblob import TextBlob
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ===== Konfigurasi =====
TELEGRAM_TOKEN = "8216938877:AAH7WKn9uJik5Hg3VJ2RIKuzTL7pqv6BIGY"
CHAT_ID =  -4881339106
NEWS_API_KEY = "c09d91931a424c518822f9b4a997e4c5"
SYMBOL = "XAUUSD"
CHECK_INTERVAL = 600  # 10 menit

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
                    news_list.append({"title": title, "link": link, "recommendation": recommendation})
    except Exception as e:
        print("Error ambil news:", e)
    return news_list

# ===== Kirim berita =====
async def broadcast_news(app):
    sent_links = set()  # menyimpan link berita yang sudah dikirim
    while True:
        news_items = await fetch_news()
        new_items = [n for n in news_items if n["link"] not in sent_links]
        if new_items:
            for news in new_items:
                text = f"{news['title']}\nRekomendasi: {news['recommendation']}\n{news['link']}"
                await app.bot.send_message(chat_id=CHAT_ID, text=text)
                sent_links.add(news["link"])
        else:
            print("Tidak ada berita baru.")
        await asyncio.sleep(CHECK_INTERVAL)

# ===== /start handler =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot aktif! Akan mengirim berita forex beserta rekomendasi buy/sell.")

# ===== Setup Bot =====
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))

# jalankan loop broadcast di background
asyncio.create_task(broadcast_news(app))

# jalankan bot polling
app.run_polling()
