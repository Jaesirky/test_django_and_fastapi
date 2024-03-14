import os

from django.http.response import JsonResponse
from django.core.asgi import get_asgi_application
from django.urls import path

from utils import get_response_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_settings')


async def test(_):
    return JsonResponse(await get_response_async())


urlpatterns = [
    path('test', test),
]

app = get_asgi_application()
