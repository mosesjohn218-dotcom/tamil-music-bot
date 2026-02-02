import os, re, asyncio, yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaAudio
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

def clean_title(title): 
    title = title.lower()
    junk = ["official","video","lyrics","hd","audio","song","music"]
    for word in junk: title = title.replace(word, "")
    return re.sub(r"[\(\[].*?[\)\]]", "", title).strip().title()

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    await update.message.reply_text("🔍 Searching...")
    
    ydl_opts = {"quiet": True, "extract_flat": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch10:{query} songs", download=False)
        results = info["entries"][:10] if info and "entries" in info else []
    
    if not results:
        await update.message.reply_text("❌ No songs found.")
        return
    
    buttons = [[InlineKeyboardButton(text=f"🎵 {clean_title(v.get('title','Unknown'))[:40]}", callback_data=f"d|{v.get('id')}")] for v in results]
    await update.message.reply_text("🎶 Select song:", reply_markup=InlineKeyboardMarkup(buttons))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data.startswith("d|"):
        video_id = query.data.split("|")[1]
        await query.answer()
        status_msg = await query.message.reply_text("🔄 Getting audio...")
        
        try:
            # DIRECT AUDIO STREAM - NO FFMPEG NEEDED!
            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://youtube.com/watch?v={video_id}", download=False)
                audio_url = info['url']
                title = info.get('title', 'Song')
            
            await status_msg.edit_text("🎵 Streaming song...")
            await query.message.reply_audio(
                audio=audio_url,
                title=title[:100],
                performer="Tamil Music Bot",
                caption=f"🎵 {title[:50]}",
                duration=info.get('duration', 0)
            )
            await status_msg.delete()
            
        except Exception as e:
            await status_msg.edit_text(f"❌ Error: {str(e)[:100]}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(CallbackQueryHandler(handle_callback))
print("🎧 Tamil Music Bot LIVE - NO FFMPEG!")
app.run_polling()
