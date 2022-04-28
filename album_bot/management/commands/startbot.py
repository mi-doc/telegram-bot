from django.core.management.base import BaseCommand
from ...bot import start_album_bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Starting echo bot. AUUUUUGA')
        start_album_bot()

