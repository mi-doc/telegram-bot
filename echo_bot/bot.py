import telebot
import os

TOKEN = os.getenv('TELEGRAM_TOKEN', None)
bot = telebot.TeleBot(TOKEN, parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Bot is listening to you.")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


def start_echo_bot():
    bot.infinity_polling()
