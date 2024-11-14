from rest_framework.routers import SimpleRouter
from users.views import UserViewSet
from django.urls import path, include

router = SimpleRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]