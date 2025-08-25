import fix_imghdr   # Patch imghdr dulu, biar telegram nggak error
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, CallbackContext
import yt_dlp
import os

TOKEN = os.getenv("8269491157:AAE2zg2z4qkrU-ODxEpAg1jPvbRZUo952nE")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Kirim link YouTube dan saya akan ubah jadi MP3!")

def download_mp3(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    update.message.reply_text("⏳ Sedang download...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'download.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file_path = "download.mp3"
        with open(file_path, "rb") as f:
            update.message.reply_audio(audio=InputFile(f))

        os.remove(file_path)
    except Exception as e:
        update.message.reply_text(f"❌ Error: {e}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("mp3", download_mp3))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
