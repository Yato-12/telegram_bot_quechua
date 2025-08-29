from keep_alive import keep_alive
import os
import json
import random
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# === Cargar variables del archivo .env ===
load_dotenv()
TOKEN = os.getenv("BOTQUECHUA_TOKEN")

# === Nombre del archivo JSON ===
JSON_FILE = "frases_quechua.json"

# === Cargar frases ===
try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        phrases = json.load(f)
    print("Se encontró frases_quechua.json.")
except FileNotFoundError:
    print(f"❌ Error: No se encontró el archivo {JSON_FILE}. Asegúrate de que está en el mismo directorio.")
    phrases = []

# Obtener las categorías del archivo JSON para los botones
categories = list(set([f["categoria"] for f in phrases]))
categories.sort() # Ordenar las categorías alfabéticamente

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not categories:
        await update.message.reply_text("❌ No hay categorías disponibles. Asegúrate de que el archivo JSON no está vacío.")
        return
    
    keyboard = [
        [InlineKeyboardButton(cat, callback_data=cat)] for cat in categories
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "¡Hola! Soy tu bot de frases en quechua.\n\n"
        "➡ Usa /frase para obtener una frase aleatoria.\n"
        "➡ O elige una categoría:",
        reply_markup=reply_markup
    )

# === /frase (aleatoria global) ===
async def frase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not phrases:
        await update.message.reply_text("❌ No hay frases disponibles en el archivo JSON.")
        return

    entry = random.choice(phrases)
    await update.message.reply_text(
        f"**{entry['categoria']}**\n\n"
        f"**Quechua:** {entry['frase_quechua']}\n"
        f"**Español:** {entry['traduccion_espanol']}",
        parse_mode="Markdown"
    )

# === Handler de botones (categorías) ===
async def categoria_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    categoria = query.data
    frases_filtradas = [f for f in phrases if f["categoria"] == categoria]

    if frases_filtradas:
        entry = random.choice(frases_filtradas)
        await query.edit_message_text(
            f"**{categoria}**\n\n"
            f"**Quechua:** {entry['frase_quechua']}\n"
            f"**Español:** {entry['traduccion_espanol']}",
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text(f"No hay frases en la categoría {categoria}.")

# === Main ===
def main():
    if not TOKEN:
        raise ValueError("❌ No se encontró TELEGRAM_TOKEN en el archivo .env")
    
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("frase", frase))
    app.add_handler(CallbackQueryHandler(categoria_handler))

    print("Bot corriendo...")
    app.run_polling()

if __name__ == "__main__":
    main()
