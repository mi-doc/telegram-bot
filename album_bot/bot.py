import os

import telebot
from telebot import types
from celery import shared_task

from .models import Album, Image, UserState

TOKEN = os.getenv('TELEGRAM_TOKEN', None)


# @shared_task
def start_album_bot():
    bot = telebot.TeleBot(TOKEN, parse_mode=None)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "Bot is listening to you.")

    @bot.message_handler(commands=['showAll'])
    def send_all(message):
        images = Image.objects.get_images_with_files_uploaded()
        if not images:
            bot.reply_to(message, 'No images here yet')

        while images:
            medias = []
            for image in images[:10]:
                img_path = f'staticfiles{image.image.url}'
                img = open(img_path, 'rb')
                medias.append(types.InputMediaPhoto(img))
            bot.send_media_group(message.chat.id, medias)
            images = images[10:]

    @bot.message_handler(commands=['albums'])
    def show_album(message):
        keyboard = types.InlineKeyboardMarkup()
        albums = Album.objects.all()
        buttons = []
        for album in albums:
            buttons.append(types.InlineKeyboardButton(text=album.name, callback_data=f"album_id__{album.pk}"))
        keyboard.add(*buttons)
        bot.send_message(message.chat.id, 'Chose an album', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('album_id'))
    def callback_inline(call):
        album_pk = call.data.split('__')[1]
        images = Image.get_all_album_images(album_id=album_pk)
        if not images:
            bot.send_message(call.message.chat.id, 'No images here yet')

        while images:
            medias = []
            for image in images[:10]:
                img_path = f'staticfiles{image.image.url}'
                img = open(img_path, 'rb')
                # bot.send_photo(call.message.chat.id, img)
                medias.append(types.InputMediaPhoto(img))
            bot.send_media_group(call.message.chat.id, medias)
            images = images[10:]

    # @bot.message_handler(commands=['resize'])
    # def resize_image(message):
    #     i = Image.objects.get_images_with_files_uploaded()[10]

    # User uploading new photo
    @bot.message_handler(content_types=['photo'])
    def upload_photo(message):
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        img_name = file_info.file_path.split('/')[-1]

        image = Image.create_from_telegram_data(image_name=img_name, downloaded_file=downloaded_file,
                                                user_id=message.from_user.id, media_group_id=message.media_group_id)

        # If we already have an image with similar media_group_id that means we are processing a set of images
        # and will automatically assign them to the same album name as the first image
        mgid = message.media_group_id
        if mgid and Image.objects.filter(media_group_id=mgid).count() > 1:
            # Sometimes image instances are created almost simultaneously, so we have to compare their IDs
            # to find out if it is the first image of an album or not
            if image.pk > Image.objects.filter(media_group_id=mgid).order_by('pk').first().pk:
                return True

        UserState.update_user_state_to_sent_photo(user_id=message.from_user.id)
        keyboard = types.InlineKeyboardMarkup()
        albums = Album.objects.all()
        buttons = []
        buttons.append(types.InlineKeyboardButton(text='Create new album', callback_data='album__create_new'))
        for album in albums:
            buttons.append(types.InlineKeyboardButton(text=album.name, callback_data=f"album__{album.pk}"))
        keyboard.add(*buttons)
        bot.send_message(message.chat.id, 'Pick a album to attach it to or chose to create a new one',
                         reply_markup=keyboard)

    @bot.message_handler(func=lambda message: True)
    def send_image_buttons(message):
        user_id = message.from_user.id
        # Check if user has sent a photo (i.e. user's state is 'sent_photo'),
        # so the next user's message should be the album of photo
        user_state = UserState.get_for_user_id(user_id=user_id).state
        if user_state == UserState.State.SENT_PHOTO:
            # Getting the last image sent by user from DB
            image = Image.get_last_image_sent_by_user(user_id=user_id)
            # Assign it so specified album
            image.assign_to_album(album_name=message.text, media_group_id=image.media_group_id)
            # Return the user's state back to initial
            UserState.update_user_state_to_init(user_id=user_id)
            text = 'image' if not image.media_group_id else 'images'
            bot.send_message(message.chat.id, f'Album of the {text} is successfully specified')

        elif user_state == UserState.State.CREATE_NEW_SUBJECT:
            if album := Album.objects.filter(user_id=user_id, name=message.text):
                alb = album.first()
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(
                    types.InlineKeyboardButton(text=f"Use {alb.name}", callback_data=f'album__{alb.pk}')
                )

                bot.reply_to(message, 'Album already exists. Write another or keep it', reply_markup=keyboard)

            else:
                # Getting the last image sent by user from DB
                image = Image.get_last_image_sent_by_user(user_id=user_id)
                image.assign_to_album(album_name=message.text, media_group_id=image.media_group_id)
                # Return the user's state back to initial
                UserState.update_user_state_to_init(user_id=user_id)
                text = 'image' if not image.media_group_id else 'images'
                bot.send_message(message.chat.id, f'Album of the {text} is successfully specified')

        else:
            # Show buttons with all images
            keyboard = types.InlineKeyboardMarkup()
            images = Image.objects.get_images_with_files_uploaded()
            buttons = []
            for image in images:
                if image.album:
                    text = f"{image.album.name} - {image.pk}"
                else:
                    text = image.pk
                buttons.append(types.InlineKeyboardButton(text=text, callback_data=image.pk))
            keyboard.add(*buttons)
            bot.send_message(message.chat.id, 'Pick image', reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('album'))
    def callback_inline(call):
        album_id_or_create = call.data.split('__')[1]
        if album_id_or_create == 'create_new':
            UserState.update_user_state(user_id=call.from_user.id, new_state=UserState.State.CREATE_NEW_SUBJECT)
            bot.send_message(call.message.chat.id, 'Please specify a name')
        else:
            image = Image.get_last_image_sent_by_user(user_id=call.from_user.id)
            album = Album.objects.get(pk=album_id_or_create)
            # If it is a part of a media group, we will assign album to the whole album
            image.assign_to_album(album_instance=album, media_group_id=image.media_group_id)
            UserState.update_user_state_to_init(user_id=call.from_user.id)
            bot.send_message(call.message.chat.id, f'The image is assigned to {album.name}')

    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        image = Image.objects.get(id=call.data)

        img_path = f'staticfiles{image.image.url}'
        img = open(img_path, 'rb')
        bot.send_photo(call.message.chat.id, img)

    bot.infinity_polling()
