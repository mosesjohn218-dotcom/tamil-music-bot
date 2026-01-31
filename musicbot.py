from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

WELCOME_TEXT = """
🎧 Tamil Music Bot
Type a movie or song name to start.

Powered by NewTamil AI
"""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.lower() in ["/start", "start"]:
        await update.message.reply_text(WELCOME_TEXT)
        return

    await update.message.reply_text(
        f"🔍 Searching for: {text}\n\n(Real song search coming next)"
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🎧 Tamil Music Bot Running...")
app.run_polling()
