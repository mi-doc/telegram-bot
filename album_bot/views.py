from django.http import HttpResponse
from .tasks import start_bot


def index(response):
    start_bot()
    return HttpResponse('The bot has been activated')