from django.apps import AppConfig
import sys
import os


class EchoBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'echo_bot'

    def ready(self):
        if 'runserver' not in sys.argv:
            '''
            We need to launch bot only once after django server starts. Otherwise it will start
            multiple times when this module is imported.
            '''
            return True


        state = int(os.getenv('ECHO_BOT_STARTED', None))
        if state:
            return True

        from .tasks import start_bot
        start_bot()
        os.environ['ECHO_BOT_STARTED'] = '1'

