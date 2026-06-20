import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# 🔑 CONFIG
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

# 🧠 memoria duplicati
seen = set()

# 💰 PREZZI
PRICES = {
    "Serie A": 17,
    "Premier League": 17,
    "La Liga": 17,
    "Ligue 1": 17,
    "Bundesliga": 17,
    "Eredivisie": 17,
    "National Team": 17,
    "World Cup": 17,
    "NBA": 32,
    "Kids": 19,
    "Shorts": 15,
    "Casual": 25,
    "F1": 25,
    "Retro": 19,
    "Player": 23,
    "Windbreaker": 49,
    "New Arrivals": 17
}

# 🌐 YUPOO CATEGORIE
YUPOO = {
    "Serie A": "https://www.yupoo.shop/category/Serie%20A",
    "Premier League": "https://www.yupoo.shop/category/Premier%20League",
    "La Liga": "https://www.yupoo.shop/category/Liga%20Portugal",
    "Ligue 1": "https://www.yupoo.shop/category/Ligue%201",
    "Bundesliga": "https://www.yupoo.shop/category/Bundesliga",
    "Eredivisie": "https://www.yupoo.shop/category/Dutch%20Eredivisie",
    "National Team": "https://www.yupoo.shop/category/National%20Team",
    "World Cup": "https://www.yupoo.shop/category/2026%20World%20Cup",
    "NBA": "https://www.yupoo.shop/category/NBA%20Silk%20version",
    "Kids": "https://www.yupoo.shop/category/kids'",
    "Shorts": "https://www.yupoo.shop/category/Shorts",
    "Casual": "https://www.yupoo.shop/category/Casual%20T-shirt",
    "F1": "https://www.yupoo.shop/category/F1",
    "Retro": "https://www.yupoo.shop/category/Retro",
    "Player": "https://www.yupoo.shop/category/Player",
    "Windbreaker": "https://www.yupoo.shop/category/Windbreaker",
    "New Arrivals": "https://www.yupoo.shop/category/New%20Arrivals"
}

# 🔍 SCRAPER
def scrape(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        items = []
        for img in soup.find_all("img"):
            src = img.get("src")
            alt = img.get("alt")

            if src and "http" in src:
                items.append({
                    "name": alt or "Maglia",
                    "photo": src
                })

        return items
    except:
        return []

# 🔘 BOTTONE
def keyboard(name):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Contattami", callback_data=f"contact|{name}")]
    ])

# 📤 INVIO
async def send(app, name, photo, category):
    price = PRICES.get(category, 17)

    await app.bot.send_photo(
        chat_id=GROUP_ID,
        photo=photo,
        caption=f"""🔥 NUOVA MAGLIA

🏷 {name}
📂 {category}
💰 Prezzo: {price}€
📏 Taglie: S - M - L - XL - XXL""",
        reply_markup=keyboard(name)
    )

# 🔁 SCAN
async def scan(app):
    for cat, url in YUPOO.items():
        items = scrape(url)

        for i in items:
            if i["photo"] in seen:
                continue

            seen.add(i["photo"])
            await send(app, i["name"], i["photo"], cat)

# ▶️ START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Bot attivo e online!")

# 🔄 SCAN MANUALE
async def manual_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Scan avviato...")
    await scan(context.application)
    await update.message.reply_text("✅ Scan completato")

# 💬 BOTTONE CALLBACK
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("📩 Richiesta inviata all'admin")

# 🔁 LOOP OGNI 6 ORE
async def loop(app):
    while True:
        await scan(app)
        await asyncio.sleep(21600)

# 🚀 APP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("scan", manual_scan))
app.add_handler(CallbackQueryHandler(button))

async def post_init(application):
    application.create_task(loop(application))

app.post_init = post_init

app.run_polling()
