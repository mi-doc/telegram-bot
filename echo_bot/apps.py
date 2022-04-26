import os
import sys

from django.apps import AppConfig


class EchoBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'echo_bot'

    def ready(self):
        """
        We need to launch bot only once after django server starts. Otherwise it will start
        multiple times when this module is imported.
        """
        if 'runserver' not in sys.argv:
            return True

        state = int(os.getenv('ECHO_BOT_STARTED', None))
        if state:
            return True

        # from .bot import start_echo_bot
        # start_echo_bot.delay()
        # from .tasks import start_bot
        # start_bot()

        from .bot import start_asyncio_bot
        start_asyncio_bot()
        os.environ['ECHO_BOT_STARTED'] = '1'
