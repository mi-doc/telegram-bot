from echo_bot.bot import start_echo_bot, TOKEN


def start_bot():
    start_echo_bot.delay(TOKEN)
