import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

TOKEN = os.getenv("8269491157:AAE2zg2z4qkrU-ODxEpAg1jPvbRZUo952nE")
URL = os.getenv("URL")  # contoh: https://your-app.up.railway.app

if not TOKEN:
    raise ValueError("TOKEN is not set! Please add TOKEN in Railway Variables.")

bot = Bot(token=TOKEN)
app = Flask(__name__)

# Dispatcher untuk handle update
dispatcher = Dispatcher(bot, None, workers=0)

# Command /start
def start(update, context):
    update.message.reply_text("Halo! Bot sudah aktif 🚀 via Webhook di Railway")

# Command /help
def help_command(update, context):
    update.message.reply_text("Gunakan /start untuk mencoba bot.")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Bot sedang berjalan 🚀"

if __name__ == "__main__":
    # Set webhook ke URL Railway kamu
    bot.set_webhook(f"{URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
