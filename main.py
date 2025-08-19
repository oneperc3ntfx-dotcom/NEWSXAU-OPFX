import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# =========================
# TOKEN & CHAT ID LANGSUNG
# =========================
TELEGRAM_TOKEN = "8216938877:AAH7WKn9uJik5Hg3VJ2RIKuzTL7pqv6BIGY"  # Ganti token botmu
CHAT_ID =  -4881339106                  # Ganti chat ID grup
NEWS_API_URL = "https://www.forexfactory.com/calendar?json"

# =========================
# Analisis berita XAU/USD
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
# Ambil berita terbaru XAU/USD
# =========================
last_sent_news = set()  # Simpan berita yang sudah dikirim

def get_latest_news():
    try:
        response = requests.get(NEWS_API_URL)
        data = response.json()
        news_list = data.get("events", [])[:10]
        xau_news = [n for n in news_list if "gold" in n.get("currency", "").lower() or "xau" in n.get("currency", "").lower()]
        messages = []
        high_impact_news = []
        for news in xau_news:
            news_id = news.get("id") or news.get("title")
            if news_id in last_sent_news:
                continue  # Skip jika sudah dikirim
            title = news.get("title", "No title")
            impact = news.get("impact", "Medium")
            recommendation, perc = analyze_sentiment(title)
            msg = f"📰 {title}\nImpact: {impact}\nRecommendation: {recommendation} ({perc}%)"
            messages.append((msg, impact))
            last_sent_news.add(news_id)
        return messages
    except Exception as e:
        return [(f"Error ambil news: {e}", "Medium")]

# =========================
# Kirim berita ke grup
# =========================
async def broadcast_news(app):
    news_list = get_latest_news()
    for msg, impact in news_list:
        await app.bot.send_message(chat_id=CHAT_ID, text=msg)

# =========================
# Command handler
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Saya bot XAU/USD. Ketik /news untuk mendapatkan update berita terbaru emas."
    )

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news_list = get_latest_news()
    if not news_list:
        await update.message.reply_text("Tidak ada berita XAU/USD terbaru.")
    for msg, _ in news_list:
        await update.message.reply_text(msg)

# =========================
# Scheduler untuk kirim otomatis setiap 60 menit
# =========================
async def scheduler(app):
    while True:
        news_list = get_latest_news()
        # Kirim berita berdampak tinggi langsung
        for msg, impact in news_list:
            if impact.lower() == "high":
                await app.bot.send_message(chat_id=CHAT_ID, text=msg)
        # Kirim semua berita terbaru setiap 60 menit
        await broadcast_news(app)
        await asyncio.sleep(3600)  # 3600 detik = 60 menit

# =========================
# Main
# =========================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Tambahkan command handler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news))
    
    # Jalankan scheduler di background
    app.create_task(scheduler(app))
    
    # Jalankan bot
    app.run_polling()
