# from rest_framework.routers import SimpleRouter
from django.urls import path, include

from .views import AssistantAPIView, AudioToChatAPIView, UserTasksAPIView

# router = SimpleRouter()

urlpatterns = [
    path('assistant-request/', AssistantAPIView.as_view(), name='assistant_request'),
    path('assistant-voice-request/', AudioToChatAPIView.as_view(), name='assistant_voice_request'),
    path('todo/', UserTasksAPIView.as_view(), name='user-tasks'),
]