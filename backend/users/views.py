from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model

from users.permissions import IsAdminUser
from .serializers import UserSerializer, RegisterSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    User controller/ endpoints.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        """
        Limit this action only for admins
        """
        if not request.user.is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN, data={'detail': 'Dont delete you bro'})
        return super().destroy(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Only for request.user == user or is_admin
        """
        user = self.get_object()
        if request.user.is_admin or request.user == user:
            return super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN, data={'detail': 'You are allowed to update only your profile'})

    def get_queryset(self):
        """
        Only admin users can view the list of all users.
        """
        if self.action == 'list' and not self.request.user.is_admin:
            return User.objects.none()
        return super().get_queryset()
    
    def retrieve(self, request, *args, **kwargs):
        """
        Permit get any user information only for is_admin = True or request.user == user
        """
        user = self.get_object()
        if request.user.is_admin or request.user == user:
            return super().retrieve(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN, data={'detail': 'Access is prohibited'})

    @action(
        detail=False,
        methods=['POST'],
        url_path='register',
        permission_classes=[AllowAny]
    )
    def register(self, request):
        """
        A new user registration
        """
        serializer = RegisterSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(
        detail=False,
        methods=['GET'],
        url_path='me',
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(
        detail=False,
        methods=['post'],
        url_path='set-vui-configured'
    )
    def set_vui_configured(self, request):
        user = request.user
        user.vui_configured = True
        user.save()
        return Response({"detail": "User vui_configured status updated."}, status=status.HTTP_200_OK)
    
    def get_permissions(self):
        if self.action in ['register']:
            return [AllowAny()] if settings.DEBUG else [IsAuthenticated()]
        elif self.action in ['list', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]