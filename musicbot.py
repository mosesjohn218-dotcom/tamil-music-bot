from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import os
seen_users = set()

BOT_TOKEN = os.getenv("BOT_TOKEN")

WELCOME_TEXT = """
🎧 Tamil Music Bot
Type a movie or song name to start.

Powered by NewTamil AI
"""

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Show welcome message once
    if user_id not in seen_users:
        seen_users.add(user_id)
        await update.message.reply_text(
            "👋 Welcome to Tamil Music Bot\n\n"
            "Type movie or song name to get the MP3 files 🎧"
        )

    # Continue normal search reply
    await update.message.reply_text(
        f"🔍 Searching for: {text}\n\n(Real song search coming next)"
    )


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🎧 Tamil Music Bot Running...")
app.run_polling()
