import os, re, asyncio, yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

def clean_title(title): 
    title = title.lower()
    junk = ["official","video","lyrics","hd","audio","song","music"]
    for word in junk: title = title.replace(word, "")
    return re.sub(r"[\(\[].*?[\)\]]", "", title).strip().title()

def smart_search(query):
    ydl_opts = {"quiet": True, "extract_flat": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch10:{query} songs", download=False)
        return info["entries"] if info and "entries" in info else []

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    await update.message.reply_text("🔍 Searching...")
    
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, lambda: smart_search(query))
    
    if not results:
        await update.message.reply_text("❌ No songs found.")
        return
    
    buttons = [[InlineKeyboardButton(text=f"🎵 {clean_title(v.get('title','Unknown'))[:40]}", callback_data=f"d|{v.get('id')}")] for v in results[:10]]
    await update.message.reply_text("🎶 Select song:", reply_markup=InlineKeyboardMarkup(buttons))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data.startswith("d|"):
        video_id = query.data.split("|")[1]
        await query.answer()
        await query.edit_message_text("🔄 Downloading MP3...")
        
        # FIXED YDL OPTIONS
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'song.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://youtube.com/watch?v={video_id}", download=True)
                return f"song.{info['ext']}" if info['ext'] != 'mp3' else 'song.mp3'
        
        try:
            loop = asyncio.get_event_loop()
            filename = await loop.run_in_executor(None, download)
            
            # Find MP3 file
            mp3_file = None
            for f in os.listdir('.'):
                if f.endswith('.mp3'):
                    mp3_file = f
                    break
            
            if mp3_file and os.path.exists(mp3_file):
                await query.edit_message_text("🎵 Sending MP3...")
                with open(mp3_file, 'rb') as audio:
                    await query.message.reply_audio(
                        audio=audio, 
                        title="Tamil Hit",
                        performer="Music Bot",
                        caption=f"🎵 Downloaded from YouTube"
                    )
                os.remove(mp3_file)
                await query.message.reply_text("✅ Song delivered!")
            else:
                await query.message.reply_text("❌ MP3 conversion failed!")
                
        except Exception as e:
            await query.message.reply_text(f"❌ Error: {str(e)}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(CallbackQueryHandler(handle_callback))
print("🎧 Tamil Music Bot LIVE!")
app.run_polling()
