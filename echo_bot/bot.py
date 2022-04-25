import os
from tempfile import TemporaryFile
from django.core.files.images import ImageFile
from celery import shared_task

import telebot
from django.core.files import File

from .models import Subject, Image

TOKEN = os.getenv('TELEGRAM_TOKEN', None)
# bot = telebot.TeleBot(TOKEN, parse_mode=None)
#
#
# @bot.message_handler(commands=['start', 'help'])
# def send_welcome(message):
#     bot.reply_to(message, "Bot is listening to you.")
#
#
# @bot.message_handler(commands=['photo'])
# def send_welcome(message):
#     img_path = f'staticfiles{Image.objects.first().image.url}'
#     img = open(img_path, 'rb')
#     bot.send_photo(message.chat.id, img, reply_to_message_id=message.message_id)
#     img.close()
#
#
# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
#     bot.reply_to(message, message.text)
#     print(message.text)
#
#
# @bot.message_handler(content_types=['photo'])
# def upload_photo(message):
#     file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
#     downloaded_file = bot.download_file(file_info.file_path)
#     img_temp = TemporaryFile()
#     img_temp.write(downloaded_file)
#     img_temp.flush()
#
#     s = Subject.objects.first()
#     i = Image.objects.create(
#         subject=s,
#         image=File(img_temp)
#     )
#     i.save()






@shared_task
def start_echo_bot():
    bot = telebot.TeleBot(TOKEN, parse_mode=None)

    @bot.message_handler(content_types=['photo'])
    def upload_photo(message):
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        img_temp = TemporaryFile()
        img_temp.write(downloaded_file)
        img_temp.flush()
        img_name = file_info.file_path.split('/')[-1]

        i = Image.objects.create()
        i.image.save(img_name, img_temp)
        i.save()
        bot.reply_to(message, i.image.url)

    @bot.message_handler(func=lambda message: True)
    def send_welcome(message):
        img_name = Image.objects.filter(image__icontains=message.text)
        if img_name:
            img_path = f'staticfiles{img_name.first().image.url}'
            img = open(img_path, 'rb')
            bot.send_photo(message.chat.id, img, reply_to_message_id=message.message_id)
            img.close()
        else:
            bot.reply_to(message, "Bot is listening to you. NEW CHANGE")


    bot.infinity_polling()