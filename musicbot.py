from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import os

seen_users = set()

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Show welcome message once per user
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
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("🎧 Tamil Music Bot is running...")
app.run_polling()
