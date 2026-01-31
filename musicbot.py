from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import yt_dlp
import os
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def search_youtube(query: str):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch5:{query} tamil song", download=False)
        return info.get("entries", [])


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    await update.message.reply_text("🔍 Finding movie songs...")

    # Run yt-dlp safely (VERY IMPORTANT)
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, lambda: asyncio.run(search_youtube(text)))

    if not results:
        await update.message.reply_text("❌ No songs found.")
        return

    buttons = []
    for video in results:
        title = video.get("title", "Unknown")
        video_id = video.get("id")

        buttons.append([
            InlineKeyboardButton(
                text=f"🎵 {title[:35]}",
                callback_data=f"download|{video_id}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        "🎶 Select a song to download:",
        reply_markup=reply_markup
    )


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()
