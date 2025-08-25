# bot.py

import os
import logging
from uuid import uuid4
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import yt_dlp

# Mengaktifkan logging untuk mempermudah debugging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Mengambil Token Bot dari Environment Variable
BOT_TOKEN = os.getenv("8269491157:AAE2zg2z4qkrU-ODxEpAg1jPvbRZUo952nE")
if not BOT_TOKEN:
    raise ValueError("Tidak ada BOT_TOKEN yang ditemukan! Mohon set di environment variables.")

# Fungsi untuk handler /start
def start(update: Update, context: CallbackContext) -> None:
    """Mengirim pesan sambutan ketika perintah /start dijalankan."""
    user = update.effective_user
    update.message.reply_html(
        f"Halo {user.mention_html()}!\n\nKirimkan saya link video YouTube, dan saya akan mengubahnya menjadi file audio MP3 untuk Anda.",
    )

# Fungsi utama untuk mengunduh dan mengonversi video
def download_audio(update: Update, context: CallbackContext) -> None:
    """Menangani pesan berisi link YouTube."""
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    url = update.message.text

    # Memberi tahu pengguna bahwa proses sedang berjalan
    processing_message = context.bot.send_message(
        chat_id=chat_id,
        text="⏳ Sedang memproses, mohon tunggu...",
        reply_to_message_id=message_id
    )

    try:
        # Konfigurasi untuk yt-dlp
        # Kita akan menyimpan file sementara dengan nama unik
        file_path_template = f"/tmp/{uuid4().hex}"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', # Kualitas audio 192 kbps
            }],
            'outtmpl': file_path_template, # Template path file output
            'noplaylist': True, # Tidak mengunduh playlist
            'logger': logger,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', 'Audio Unduhan')
            
        # Path file MP3 yang sebenarnya setelah konversi
        mp3_file_path = f"{file_path_template}.mp3"
        
        # Kirim file audio ke pengguna
        with open(mp3_file_path, 'rb') as audio_file:
            context.bot.send_audio(
                chat_id=chat_id,
                audio=InputFile(audio_file),
                title=video_title,
                caption=f"✅ Selesai! - @{context.bot.username}",
                reply_to_message_id=message_id
            )

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Error saat mengunduh: {e}")
        context.bot.send_message(
            chat_id=chat_id,
            text="❌ Gagal memproses link. Pastikan link YouTube valid dan tidak bersifat pribadi (private).",
            reply_to_message_id=message_id
        )
    except Exception as e:
        logger.error(f"Terjadi error tak terduga: {e}")
        context.bot.send_message(
            chat_id=chat_id,
            text="❌ Maaf, terjadi kesalahan internal. Silakan coba lagi nanti.",
            reply_to_message_id=message_id
        )
    finally:
        # Hapus pesan "sedang memproses"
        context.bot.delete_message(chat_id=chat_id, message_id=processing_message.message_id)
        # Hapus file mp3 yang sudah diunduh dari server untuk menghemat ruang
        if 'mp3_file_path' in locals() and os.path.exists(mp3_file_path):
            os.remove(mp3_file_path)


def main() -> None:
    """Mulai bot."""
    # Buat Updater dan teruskan token bot Anda.
    updater = Updater(BOT_TOKEN)

    # Dapatkan dispatcher untuk mendaftarkan handler
    dispatcher = updater.dispatcher

    # Daftarkan handler untuk perintah
    dispatcher.add_handler(CommandHandler("start", start))

    # Daftarkan handler untuk pesan teks (link YouTube)
    # Filter untuk URL, bisa dispesifikkan lagi jika perlu
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_audio))

    # Mulai Bot
    updater.start_polling()

    # Jalankan bot sampai Anda menekan Ctrl-C
    updater.idle()

if __name__ == '__main__':

    main()
