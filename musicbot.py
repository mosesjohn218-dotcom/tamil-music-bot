import os
import re
import asyncio
import yt_dlp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ---------- Title Cleaner ----------
def clean_title(title: str):
    title = title.lower()

    junk = [
        "official", "video", "lyrics", "lyric",
        "hd", "audio", "jukebox", "full",
        "song", "music"
    ]

    for word in junk:
        title = title.replace(word, "")

    title = re.sub(r"\(.*?\)", "", title)
    title = re.sub(r"\|.*", "", title)
    title = re.sub(r"\s+", " ", title)

    return title.strip().title()

# ---------- Playlist Search ----------
def search_album(query):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True
    }

    search_query = f"ytsearch1:{query} full album jukebox official"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)

        if not info or "entries" not in info:
            return []

        first = info["entries"][0]

        # If playlist found
        if "entries" in first:
            return first["entries"][:10]

        return []

# ---------- Telegram Handler ----------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()

    await update.message.reply_text("🔍 Finding movie album...")

    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, lambda: search_album(query))

    if not results:
        await update.message.reply_text("❌ Album not found.")
        return

    buttons = []

    for video in results:
        raw_title = video.get("title", "Unknown")
        video_id = video.get("id")

        title = clean_title(raw_title)

        buttons.append([
            InlineKeyboardButton(
                text=f"🎵 {title}",
                callback_data=f"download|{video_id}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "🎶 Select a song:",
        reply_markup=reply_markup
    )

# ---------- Run Bot ----------
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("🎧 Tamil Album Bot Running...")
app.run_polling()
