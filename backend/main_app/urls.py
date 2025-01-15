# from rest_framework.routers import SimpleRouter
from django.urls import path, include

from .views import AssistantAPIView

# router = SimpleRouter()

urlpatterns = [
    path('assistant-request/', AssistantAPIView.as_view(), name='assistant_request'),
]