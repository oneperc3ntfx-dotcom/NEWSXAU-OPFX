import asyncio
import requests
from telegram import Bot
from telegram.error import TelegramError

# TOKEN & chat_id grup
TOKEN = "8216938877:AAH7WKn9uJik5Hg3VJ2RIKuzTL7pqv6BIGY"
CHAT_ID = "-4881339106"  # contoh: -1001234567890
bot = Bot(token=TOKEN)

CHECK_INTERVAL = 300  # detik (5 menit)

# Ambil berita ekonomi XAU/USD dari API (dummy)
def get_news():
    berita = [
        {"judul": "Inflasi AS naik", "dampak": "high", "pair": "XAU/USD"},
        {"judul": "Federal Reserve Rate Decision", "dampak": "medium", "pair": "XAU/USD"},
    ]
    return berita

# Tentukan rekomendasi buy/sell berdasar berita
def rekomendasi(berita):
    hasil = []
    for item in berita:
        dampak = item["dampak"]
        # Konversi dampak ke presentase
        if dampak == "high":
            persen = 80
        elif dampak == "medium":
            persen = 50
        else:
            persen = 20
        
        # Rekomendasi sederhana
        if "inflasi" in item["judul"].lower() or "rate" in item["judul"].lower():
            action = "BUY" if "inflasi" in item["judul"].lower() else "SELL"
        else:
            action = "HOLD"
        
        hasil.append({
            "judul": item["judul"],
            "action": action,
            "persen": persen
        })
    return hasil

# Kirim pesan ke Telegram
def kirim_ke_telegram(rekom):
    for item in rekom:
        text = f"📰 Berita: {item['judul']}\n💹 Rekomendasi: {item['action']}\n📊 Dampak: {item['persen']}%"
        try:
            bot.send_message(chat_id=CHAT_ID, text=text)
        except TelegramError as e:
            print("Error mengirim pesan:", e)

# Looping asynchronous untuk update otomatis
async def main_loop():
    while True:
        berita = get_news()
        rekom = rekomendasi(berita)
        kirim_ke_telegram(rekom)
        await asyncio.sleep(CHECK_INTERVAL)  # tunggu 5 menit

if __name__ == "__main__":
    asyncio.run(main_loop())
