import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ganti dengan token bot Anda
TELEGRAM_TOKEN = "8216938877:AAH7WKn9uJik5Hg3VJ2RIKuzTL7pqv6BIGY"
CHAT_ID = " -4881339106"

# Fungsi untuk analisis berita sederhana
def analisis_berita(berita_text):
    text = berita_text.lower()
    if any(word in text for word in ["naik", "bullish", "menguat"]):
        return "BUY"
    elif any(word in text for word in ["turun", "bearish", "melemah"]):
        return "SELL"
    else:
        return "HOLD"

# Fungsi mengambil berita (contoh)
async def ambil_berita():
    # Simulasi berita
    return [
        {"symbol": "XAUUSD", "headline": "Harga emas menguat karena dolar melemah", "impact": "high"},
        {"symbol": "EURUSD", "headline": "Euro stabil hari ini", "impact": "low"}
    ]

# Fungsi broadcast ke Telegram
async def broadcast_news(app):
    try:
        berita_list = await ambil_berita()
        for berita in berita_list:
            rekomendasi = analisis_berita(berita["headline"])
            msg = f"{berita['symbol']} - {berita['headline']}\nRekomendasi: {rekomendasi}"
            # Jika dampak tinggi, kirim langsung
            if berita["impact"] == "high":
                await app.bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print("Error broadcast:", e)

# Scheduler untuk kirim berita setiap 60 menit
async def scheduler(app):
    while True:
        await broadcast_news(app)
        await asyncio.sleep(60 * 60)  # 60 menit

# Handler untuk /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot aktif! Siap mengirim berita dan rekomendasi forex.")

# Main
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # Jalankan scheduler
    asyncio.create_task(scheduler(app))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
