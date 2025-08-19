import asyncio
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from textblob import TextBlob
import aiohttp
import time

# --- Konfigurasi ---
TOKEN = "8216938877:AAH7WKn9uJik5Hg3VJ2RIKuzTL7pqv6BIGY"
CHAT_ID = " -4881339106"
NEWS_API_URL = "https://api.example.com/news?symbol=XAUUSD"  # Ganti dengan API asli
INTERVAL = 60 * 60  # 60 menit

# --- Fungsi Analisis Sentimen ---
def analisis_berita(berita_text):
    blob = TextBlob(berita_text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "BUY"
    elif polarity < -0.1:
        return "SELL"
    else:
        return "HOLD"

# --- Fungsi Ambil Berita ---
async def ambil_berita():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(NEWS_API_URL) as response:
                if response.status != 200:
                    print(f"Error ambil berita: {response.status}")
                    return []
                data = await response.json()
                return data.get("news", [])
        except Exception as e:
            print(f"Exception ambil berita: {e}")
            return []

# --- Fungsi Kirim Berita ke Telegram ---
async def kirim_berita(bot: Bot, berita_text, high_impact=False):
    rekomendasi = analisis_berita(berita_text)
    msg = f"Berita Forex terbaru:\n{berita_text}\n\nRekomendasi: {rekomendasi}"
    await bot.send_message(chat_id=CHAT_ID, text=msg)
    if high_impact:
        print("Dampak tinggi: dikirim langsung!")

# --- Scheduler Berita ---
async def scheduler(app):
    while True:
        news_list = await ambil_berita()
        for berita in news_list:
            text = berita.get("title", "")
            impact = berita.get("impact", "low")  # contoh: 'high' atau 'low'
            if impact == "high":
                await kirim_berita(app.bot, text, high_impact=True)
            else:
                # Bisa simpan dulu, dikirim nanti setiap 60 menit
                await kirim_berita(app.bot, text)
        await asyncio.sleep(INTERVAL)

# --- Handler /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot aktif ✅. Siap mengirim berita dan rekomendasi.")

# --- Main ---
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # Jalankan scheduler di background
    asyncio.create_task(scheduler(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
