import os
import re
import yt_dlp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

seen_users = set()

# ---------- CLEAN TITLE ----------
def clean_title(title: str):
    title = title.lower()

    junk_words = [
        "video", "lyric", "lyrics", "song", "jukebox",
        "hd", "official", "audio", "music", "full"
    ]

    for word in junk_words:
        title = title.replace(word, "")

    title = re.sub(r"\(.*?\)", "", title)
    title = re.sub(r"\|.*", "", title)
    title = title.replace("-", " ")
    title = re.sub(r"\s+", " ", title)

    return title.strip().title()

# ---------- YOUTUBE SEARCH ----------
def search_youtube(query):

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
        "default_search": "ytsearch10",
        "source_address": "0.0.0.0"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch10:{query}", download=False)
        return info.get("entries", [])

# ---------- MAIN ----------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in seen_users:
        seen_users.add(user_id)
        await update.message.reply_text(
            "👋 Welcome to Tamil Music Bot\n\n"
            "Type movie or song name to get the MP3 files 🎧"
        )

    await update.message.reply_text("🔍 Finding movie songs...")

    query = f"{text} tamil movie song"

    results = search_youtube(query)

    if not results:
        await update.message.reply_text("❌ No songs found.")
        return

    buttons = []

    for video in results:
        raw_title = video.get("title", "Unknown")
        title = clean_title(raw_title)
        video_id = video.get("id")

        buttons.append([
            InlineKeyboardButton(
                text=f"🎵 {title[:35]}",
                callback_data=f"download|{video_id}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "🎶 Select a song:",
        reply_markup=reply_markup
    )

# ---------- RUN ----------
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("🎧 Tamil Music Bot Running...")
app.run_polling()
