import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

# PERFECT TITLE CLEANER
def clean_title(title):
    if not title:
        return "Tamil Hit"
    title = title.lower()
    junk = ["official", "video", "lyrics", "lyric", "hd", "full", "audio", "song", "music", "4k", "1080p"]
    for word in junk:
        title = re.sub(rf'\b{re.escape(word)}\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'[\[\(].*?[\]\)]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title.title()[:50]

# SIMPLE YOUTUBE SEARCH (Railway-friendly)
async def search_songs(query, limit=8):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
            'source_address': '0.0.0.0'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch{limit}:{query} tamil song"
            info = ydl.extract_info(search_query, download=False)
            return info.get('entries', []) if info else []
    except:
        return []

# MAIN TEXT HANDLER
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    await update.message.reply_text("🔍 Searching Tamil songs...")
    
    results = await search_songs(query)
    
    if not results:
        await update.message.reply_text("❌ No Tamil songs found!\nTry: `master`, `jailer`, `leo`")
        return
    
    # CREATE BEAUTIFUL BUTTONS
    buttons = []
    for i, video in enumerate(results[:8]):
        title = clean_title(video.get('title', 'Unknown Song'))
        video_id = video.get('id', f'id{i}')
        buttons.append([InlineKeyboardButton(f"🎵 {title}", callback_data=f"dl|{video_id}")])
    
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(f"🎶 Found {len(buttons)} songs for '{query}'", reply_markup=keyboard)

# DOWNLOAD HANDLER (Railway-optimized)
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('dl|'):
        video_id = query.data.split('|')[1]
        status_msg = await query.message.reply_text("🎵 Preparing high-quality audio...")
        
        try:
            # RAILWAY-SAFE YOUTUBE-DLP
            ydl_opts = {
                'format': 'bestaudio/best[height<=480]/bestaudio',
                'outtmpl': 'audio.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://youtube.com/watch?v={video_id}", download=True)
                title = info.get('title', 'Tamil Song')
            
            # SEND AUDIO FILE
            audio_file = None
            for file in os.listdir('.'):
                if file.startswith('audio') and file.endswith(('.mp3', '.m4a', '.webm')):
                    audio_file = file
                    break
            
            if audio_file:
                await status_msg.edit_text("🚀 Sending song...")
                with open(audio_file, 'rb') as audio:
                    await query.message.reply_audio(
                        audio=audio,
                        title=clean_title(title),
                        performer="Tamil Music Bot 🎵",
                        caption=f"🎧 {clean_title(title)}\n💾 High Quality Audio"
                    )
                os.remove(audio_file)
                await status_msg.delete()
            else:
                await status_msg.edit_text("❌ Audio processing failed!")
                
        except Exception as e:
            await status_msg.edit_text(f"❌ Failed to process\nTry another song!\n\nError: {str(e)[:80]}")

# START COMMAND
async def start(update: Update, context):
    welcome = """
🎧 **Tamil Music Bot v2.0** 🎧

Send any Tamil song name:
`master` `jailer` `leo` `ala`

**Examples:**
• `vaathi coming`
• `kaavaalaa`
• `naa ready`

🔥 **High quality MP3s!**
"""
    await update.message.reply_text(welcome)

# BUILD & RUN
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # HANDLERS
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("🎧 Tamil Music Bot LIVE on Railway!")
    app.run_polling()

if __name__ == "__main__":
    main()
