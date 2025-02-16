from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()  # returns a custom user models specified in the AUTH_USER_MODEL settings.py

class UserSerializer(serializers.ModelSerializer):  # To serialize user info
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'vui_configured', 'is_admin', 'ttm_stage']

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(  # Additional email validation even though validation on the db level is already set in the model
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="This email has already been registered")]
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])  # embedded validator for passwords
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            return serializers.ValidationError({"password": "Passwords do not match bro. Try again"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            email = validated_data['email'],
            password = validated_data['password']
        )
        return user
    
    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        tokens = self.get_token_for_user(instance)
        data.update(tokens)
        return data
