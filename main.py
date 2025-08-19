import asyncio
import requests
from telegram import Bot
from telegram.ext import ApplicationBuilder

# ====== CONFIG ======
TELEGRAM_TOKEN = "8216938877:AAH7WKn9uJik5Hg3VJ2RIKuzTL7pqv6BIGY"
CHAT_ID =  -4881339106  # ganti dengan ID grup Telegram
NEWS_API_URL = "https://api.example.com/news?symbol=XAUUSD"
HIGH_IMPACT = ["High"]  # level dampak yang dianggap tinggi

# ====== INISIALISASI BOT ======
bot = Bot(token=TELEGRAM_TOKEN)
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# ====== FUNCTION AMBIL NEWS ======
def get_news():
    try:
        response = requests.get(NEWS_API_URL, timeout=10)
        if response.status_code != 200 or not response.text:
            print("Error ambil news:", response.status_code, response.text)
            return []
        data = response.json()
        return data.get("news", [])
    except Exception as e:
        print("Exception ambil news:", e)
        return []

# ====== FUNCTION BROADCAST ======
async def broadcast_news():
    news_list = get_news()
    for news in news_list:
        impact = news.get("impact", "")
        msg = f"📰 {news.get('title', 'No Title')}\n📅 {news.get('date', '')}\nImpact: {impact}\n{news.get('link', '')}"
        try:
            await bot.send_message(chat_id=CHAT_ID, text=msg)
        except Exception as e:
            print("Error kirim ke Telegram:", e)
        # Kirim langsung jika high impact
        if impact in HIGH_IMPACT:
            print("High impact news dikirim langsung!")

# ====== SCHEDULER ======
async def scheduler():
    while True:
        try:
            print("Cek berita XAUUSD...")
            await broadcast_news()
        except Exception as e:
            print("Error scheduler:", e)
        # Tunggu 60 menit
        await asyncio.sleep(3600)

# ====== START BOT ======
async def main():
    # Jalankan scheduler
    asyncio.create_task(scheduler())
    # Jalankan bot polling (untuk menerima perintah jika diperlukan)
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
