import telegram
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
import urllib.request
import json
import ssl
import asyncio
import datetime

context = ssl._create_unverified_context()
harga_terakhir = {"bitcoin": None, "peaq": None, "pepe": None}

def get_crypto_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
    try:
        with urllib.request.urlopen(url, timeout=10, context=context) as response:
            data = json.loads(response.read())
            return data.get(coin_id, {})
    except:
        return {}

def format_harga(coin_id, nama):
    data = get_crypto_price(coin_id)
    if not data:
        return f"Data {nama} tidak ditemukan."
    harga = data.get("usd", 0)
    perubahan = data.get("usd_24h_change", 0)
    emoji = "🟢" if perubahan >= 0 else "🔴"
    return f"{emoji} *{nama}*: ${harga:,.6f}\n24j: {perubahan:+.2f}%"

async def start_cmd(update, context):
    await update.message.reply_text(
        "🤖 *Agen Pemantau*\n\n"
        "/harga - Cek BTC, PEAQ, PEPE\n"
        "/pantau - Aktifkan pemantauan",
        parse_mode="Markdown"
    )

async def harga_cmd(update, context):
    await update.message.reply_text("⏳ Mengambil data...")
    btc = format_harga("bitcoin", "BTC")
    peaq = format_harga("peaq", "PEAQ")
    pepe = format_harga("pepe", "PEPE")
    await update.message.reply_text(f"{btc}\n\n{peaq}\n\n{pepe}", parse_mode="Markdown")

async def pantau_cmd(update, context):
    await update.message.reply_text("✅ Pemantauan otomatis diaktifkan.")

async def pantau_harga(app):
    while True:
        await asyncio.sleep(300)  # 5 menit
        for coin_id, nama in [("bitcoin", "BTC"), ("peaq", "PEAQ"), ("pepe", "PEPE")]:
            data = get_crypto_price(coin_id)
            if data:
                harga_sekarang = data.get("usd", 0)
                if harga_terakhir[coin_id]:
                    perubahan = ((harga_sekarang - harga_terakhir[coin_id]) / harga_terakhir[coin_id]) * 100
                    if abs(perubahan) > 3:
                        emoji = "🚀" if perubahan > 0 else "⚠️"
                        await app.bot.send_message(
                            chat_id=CHAT_ID_KAMU,
                            text=f"{emoji} *{nama}* berubah {perubahan:+.2f}%!\nHarga: ${harga_sekarang:,.6f}",
                            parse_mode="Markdown"
                        )
                harga_terakhir[coin_id] = harga_sekarang

async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("harga", harga_cmd))
    app.add_handler(CommandHandler("pantau", pantau_cmd))
    print("Agen pemantau berjalan...")
    await app.initialize()
    await app.updater.start_polling()
    asyncio.create_task(pantau_harga(app))
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
