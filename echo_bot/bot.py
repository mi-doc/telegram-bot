import os
from tempfile import TemporaryFile

import telebot
from telebot import types
from celery import shared_task

from .models import Image

TOKEN = os.getenv('TELEGRAM_TOKEN', None)


@shared_task
def start_echo_bot():
    bot = telebot.TeleBot(TOKEN, parse_mode=None)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "Bot is listening to you.")

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
            # bot.reply_to(message, "Bot is listening to you. NEW CHANGE")
            keyboard = types.InlineKeyboardMarkup()
            images = Image.objects.all()
            buttons = []
            for image in images:
                if not image.image or not image.image.url:
                    continue

                if image.subject:
                    text = f"{image.subject.name} - {image.pk}"
                else:
                    text = image.pk
                buttons.append(types.InlineKeyboardButton(text=text, callback_data=image.pk))
            keyboard.add(*buttons)

            bot.send_message(message.chat.id, 'Images', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        # img_instance = Image.objects.get(id=call.data)
        images = Image.objects.get_images_with_files_uploaded()[:10]
        medias = []
        for image in images:
            img_path = f'staticfiles{image.image.url}'
            img = open(img_path, 'rb')
            # bot.send_photo(call.message.chat.id, img)
            medias.append(types.InputMediaPhoto(img))

        bot.send_media_group(call.message.chat.id, medias)

    bot.infinity_polling()
