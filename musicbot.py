import os
import asyncio
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import yt_dlp

# ======================
# BOT TOKEN (Railway ENV)
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ======================
# CLEAN TITLE FUNCTION
# ======================
def clean_title(title: str):
    title = title.lower()

    junk_words = [
        "video", "lyric", "lyrics", "song", "jukebox",
        "hd", "official", "audio", "music", "full",
        "thalapathy", "vijay", "anirudh", "sony", "t-series"
    ]

    for word in junk_words:
        title = title.replace(word, "")

    title = re.sub(r"\(.*?\)", "", title)
    title = re.sub(r"\|.*", "", title)
    title = title.replace("-", " ")
    title = re.sub(r"\s+", " ", title)

    return title.strip().title()

# ======================
# YOUTUBE SEARCH
# ======================
async def search_youtube(query):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
    }

    def _search():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch8:{query}", download=False)
            return info.get("entries", [])

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _search)

# ======================
# MESSAGE HANDLER
# ======================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()

    results = await search_youtube(query)

    if not results:
        await update.message.reply_text("❌ No songs found.")
        return

    buttons = []

    for video in results:
        raw_title = video.get("title", "Unknown")
        video_id = video.get("id")

        clean = clean_title(raw_title)

        buttons.append([
            InlineKeyboardButton(
                text=f"🎵 {clean}",
                callback_data=f"yt|{video_id}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "🎶 Select a song:",
        reply_markup=reply_markup
    )

# ======================
# BOT START
# ======================
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("🎧 Tamil Music Bot Running...")
app.run_polling()
