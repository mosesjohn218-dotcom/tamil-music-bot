from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import os
import subprocess
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")

# -------- Helpers --------

def clean_title(title: str) -> str:
    title = re.sub(r"\(.*?\)|\[.*?\]", "", title)
    title = re.sub(
        r"official|video|lyrical|audio|song|tamil|movie",
        "",
        title,
        flags=re.I
    )
    return title.strip().title()

def get_movie_songs(movie: str, limit=6):
    query = f"ytsearch15:{movie} movie songs"
    cmd = ["yt-dlp", "--get-title", query]
    result = subprocess.run(cmd, capture_output=True, text=True)

    songs, seen = [], set()
    for t in result.stdout.splitlines():
        name = clean_title(t)
        if name and name not in seen:
            seen.add(name)
            songs.append(name)
        if len(songs) >= limit:
            break
    return songs

# -------- Handlers --------

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie = update.message.text.strip()
    await update.message.reply_text("🔎 Finding movie songs…")

    songs = get_movie_songs(movie)

    if not songs:
        await update.message.reply_text("❌ No songs found.")
        return

    buttons = []
    for song in songs:
        buttons.append(
            [InlineKeyboardButton(f"🎵 {song}", callback_data=f"{movie}|{song}")]
        )

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        f"🎬 *{movie.title()} – Movie Songs*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    movie, song = data.split("|", 1)

    await update.callback_query.message.reply_text(
        f"⏬ Downloading: *{song}*\n\n(MP3 coming next)",
        parse_mode="Markdown"
    )

# -------- App --------

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(CallbackQueryHandler(handle_button))

print("🎧 Tamil Music Bot Running (Buttons Mode)...")
app.run_polling()
