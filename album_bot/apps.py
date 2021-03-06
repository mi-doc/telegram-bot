import os
import sys

from django.apps import AppConfig


class EchoBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'album_bot'

    def ready(self):
        """
        For debug environment. 
        We need to launch bot only once after django server starts. Otherwise it will start
        multiple times when this module is imported.
        """
        if 'runserver' not in sys.argv:
            return True

        bot_already_started = bool(int(os.getenv('ECHO_BOT_STARTED', 0)))
        if bot_already_started:
            return True

        # from .bot import start_album_bot
        # start_album_bot.delay()
        from .tasks import start_bot
        os.environ['ECHO_BOT_STARTED'] = '1'
        start_bot()

