import os
from tempfile import TemporaryFile

import telebot
from telebot import types
from celery import shared_task

from .models import Subject, Image, UserState

TOKEN = os.getenv('TELEGRAM_TOKEN', None)


# @shared_task
def start_album_bot():
    bot = telebot.TeleBot(TOKEN, parse_mode=None)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "Bot is listening to you.")

    @bot.message_handler(commands=['album'])
    def send_album(message):
        images = Image.objects.get_images_with_files_uploaded()
        if not images:
            bot.reply_to(message, 'No images here yet')

        while images:
            medias = []
            for image in images[:10]:
                img_path = f'staticfiles{image.image.url}'
                img = open(img_path, 'rb')
                # bot.send_photo(call.message.chat.id, img)
                medias.append(types.InputMediaPhoto(img))
            bot.send_media_group(message.chat.id, medias)
            images = images[10:]

    # @bot.message_handler(commands=['resize'])
    # def resize_image(message):
    #     i = Image.objects.get_images_with_files_uploaded()[10]


    @bot.message_handler(content_types=['photo'])
    def upload_photo(message):
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        img_temp = TemporaryFile()
        img_temp.write(downloaded_file)
        img_temp.flush()
        img_name = file_info.file_path.split('/')[-1]

        i = Image.objects.create(user_id=message.from_user.id)
        i.image.save(img_name, img_temp)
        i.save()
        UserState.update_user_state_to_sent_photo(user_id=message.from_user.id)

        keyboard = types.InlineKeyboardMarkup()
        subjects = Subject.objects.all()
        buttons = []
        buttons.append(types.InlineKeyboardButton(text='Create new subject', callback_data='subject__create_new'))
        for subject in subjects:
            buttons.append(types.InlineKeyboardButton(text=subject.name, callback_data=f"subject__{subject.pk}"))
        keyboard.add(*buttons)
        bot.send_message(message.chat.id, 'Pick a subject to attach it to of chose to create a new one',
                         reply_markup=keyboard)

    @bot.message_handler(func=lambda message: True)
    def send_image_buttons(message):
        user_id = message.from_user.id

        # Check if user has sent a photo (i.e. user's state is 'sent_photo'),
        # so the next user's message should be the subject of photo
        user_state = UserState.get_for_user_id(user_id=user_id).state
        if user_state == UserState.State.SENT_PHOTO:
            # Getting the last image sent by user from DB
            image = Image.get_last_image_sent_by_user(user_id=user_id)
            # Assign it so specified subject
            image.assign_to_subject(subject_name=message.text)
            # Return the user's state back to initial
            UserState.update_user_state_to_init(user_id=user_id)
            bot.send_message(message.chat.id, 'Subject of the image is successfully specified')

        elif user_state == UserState.State.CREATE_NEW_SUBJECT:
            if subject := Subject.objects.filter(user_id=user_id, name=message.text):
                sub = subject.first()
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(
                    types.InlineKeyboardButton(text=f"Use {sub.name}", callback_data=f'subject__{sub.pk}')
                )

                bot.reply_to(message, 'Subject already exists. Write another or chose this', reply_markup=keyboard)

            else:
                subject = Subject.objects.create(user_id=user_id, name=message.text)
                # Getting the last image sent by user from DB
                image = Image.get_last_image_sent_by_user(user_id=user_id)
                # Assign it so specified subject
                image.subject = subject
                image.save()
                # Return the user's state back to initial
                UserState.update_user_state_to_init(user_id=user_id)
                bot.send_message(message.chat.id, 'Subject of the image is successfully specified')

        else:
            keyboard = types.InlineKeyboardMarkup()
            images = Image.objects.get_images_with_files_uploaded()
            buttons = []
            for image in images:
                if image.subject:
                    text = f"{image.subject.name} - {image.pk}"
                else:
                    text = image.pk
                buttons.append(types.InlineKeyboardButton(text=text, callback_data=image.pk))
            keyboard.add(*buttons)
            bot.send_message(message.chat.id, 'Pick image', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('subject'))
    def callback_inline(call):
        subject_id_or_create = call.data.split('__')[1]
        if subject_id_or_create == 'create_new':
            UserState.update_user_state(user_id=call.from_user.id, new_state=UserState.State.CREATE_NEW_SUBJECT)
            bot.send_message(call.message.chat.id, 'Please specify a name')
        else:
            image = Image.get_last_image_sent_by_user(user_id=call.from_user.id)
            subject = Subject.objects.get(pk=subject_id_or_create)
            image.assign_to_subject(subject_instance=subject)
            UserState.update_user_state_to_init(user_id=call.from_user.id)
            bot.send_message(call.message.chat.id, f'The image is assigned to {subject.name}')

    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        image = Image.objects.get(id=call.data)

        img_path = f'staticfiles{image.image.url}'
        img = open(img_path, 'rb')
        bot.send_photo(call.message.chat.id, img)

    bot.infinity_polling()
