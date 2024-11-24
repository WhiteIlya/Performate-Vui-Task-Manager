# from rest_framework.routers import SimpleRouter
from django.urls import path, include

from .views import AudioToChatView

# router = SimpleRouter()

urlpatterns = [
    path('audio-to-chat/', AudioToChatView.as_view(), name='audio_to_chat'),
]