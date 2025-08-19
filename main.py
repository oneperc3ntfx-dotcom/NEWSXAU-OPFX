import aiohttp
import asyncio
from textblob import TextBlob
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = "8216938877:AAH7WKn9uJik5Hg3VJ2RIKuzTL7pqv6BIGY"
CHAT_ID =  -4881339106
NEWS_API_KEY = "c09d91931a424c518822f9b4a997e4c5"
SYMBOL = "XAUUSD"
CHECK_INTERVAL = 600  # 10 menit

def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "BUY"
    elif polarity < -0.1:
        return "SELL"
    else:
        return "NEUTRAL"

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

async def broadcast_news(app):
    """Loop untuk mengirim berita berkala."""
    sent_links = set()
    while True:
        news_items = await fetch_news()
        new_items = [n for n in news_items if n["link"] not in sent_links]

        if new_items:
            for news in new_items:
                text = f"{news['title']}\nRekomendasi: {news['recommendation']}\n{news['link']}"
                try:
                    await app.bot.send_message(chat_id=CHAT_ID, text=text)
                    sent_links.add(news["link"])
                except Exception as e:
                    print("Gagal kirim pesan:", e)
        else:
            print("Tidak ada berita baru.")

        await asyncio.sleep(CHECK_INTERVAL)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot aktif! Akan mengirim berita forex beserta rekomendasi buy/sell.")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Jalankan loop broadcast_news sebagai background task
    asyncio.create_task(broadcast_news(app))

    # Jalankan polling bot
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
