import asyncio
import aiohttp
from textblob import TextBlob
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = "8216938877:AAH7WKn9uJik5Hg3VJ2RIKuzTL7pqv6BIGY"
CHAT_ID = " -4881339106"  # opsional jika ingin broadcast

NEWS_API_URL = "https://api.example.com/news?symbol=XAUUSD"

# Fungsi untuk ambil berita
async def fetch_news():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(NEWS_API_URL) as resp:
                data = await resp.json()
                # contoh asumsi data['articles'] list berita
                if data.get("articles"):
                    return data["articles"][0]["title"]
                return None
        except Exception as e:
            print("Exception ambil news:", e)
            return None

# Analisis sentimen sederhana untuk rekomendasi
def analyze_sentiment(text: str) -> str:
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "BUY"
    elif polarity < -0.1:
        return "SELL"
    else:
        return "HOLD"

# Scheduler untuk broadcast berita + rekomendasi
async def scheduler(app):
    while True:
        news = await fetch_news()
        if news:
            recommendation = analyze_sentiment(news)
            msg = f"Berita XAUUSD:\n{news}\nRekomendasi: {recommendation}"
            try:
                await app.bot.send_message(chat_id=CHAT_ID, text=msg)
            except Exception as e:
                print("Error kirim pesan:", e)
        else:
            print("Tidak ada berita baru.")
        await asyncio.sleep(60 * 60)  # 60 menit

# Handler /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot aktif!")

# Fungsi post_init untuk jalankan scheduler
async def on_startup(app):
    asyncio.create_task(scheduler(app))

# Build aplikasi Telegram
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.post_init = on_startup

if __name__ == "__main__":
    app.run_polling()
