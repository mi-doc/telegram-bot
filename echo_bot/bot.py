import os
from tempfile import TemporaryFile

import telebot
from django.core.files import File

from .models import Subject, Image

TOKEN = os.getenv('TELEGRAM_TOKEN', None)
bot = telebot.TeleBot(TOKEN, parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Bot is listening to you.")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


@bot.message_handler(content_types=['photo'])
def upload_photo(message):
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    img_temp = TemporaryFile()
    img_temp.write(downloaded_file)
    img_temp.flush()

    s = Subject.objects.first()
    i = Image.objects.create(
        subject=s,
        image=File(img_temp)
    )
    i.save()


def start_echo_bot():
    bot.infinity_polling()
