from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters
)
import os
import yt_dlp

BOT_TOKEN = os.getenv("BOT_TOKEN")
seen_users = set()

# --- YouTube search function ---
def search_youtube(query, limit=5):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        return info.get("entries", [])


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Welcome message (once per user)
    if user_id not in seen_users:
        seen_users.add(user_id)
        await update.message.reply_text(
            "👋 Welcome to Tamil Music Bot\n\n"
            "Type movie or song name to get the MP3 files 🎧"
        )

    await update.message.reply_text("🔎 Finding songs...")

    results = search_youtube(text)

    if not results:
        await update.message.reply_text("❌ No results found")
        return

    buttons = []
    for video in results:
        title = video.get("title", "Unknown")
        video_id = video.get("id")
        buttons.append(
            [InlineKeyboardButton(title[:50], callback_data=video_id)]
        )

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "🎵 Select a song:",
        reply_markup=reply_markup
    )


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "⬇️ Download feature coming next step 😄"
    )


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(CallbackQueryHandler(handle_button))

app.run_polling()
