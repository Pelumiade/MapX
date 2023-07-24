from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        # user = User.objects.filter(email=email).get()

        user = authenticate(email=email, password=password)

        if user is None:
            # If authentication fails, raise AuthenticationFailed exception
            raise AuthenticationFailed("Invalid email or password.")

        
        refresh_token = RefreshToken.for_user(user)
        access = str(refresh_token.access_token)
        refresh = str(refresh_token)

        if not hasattr(user, "feo"):
            payload = {
                "email": email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "designation": user.designation,
                "picture": user.picture.url if user.picture else "lol",
                "location": user.admin.location.country.name,
                "role": "Admin",
                "phone_number": user.phone_number.national_number,
                "access": access,
                "refresh": refresh,
            }
        else:
            payload = {
                "email": email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "designation": user.designation,
                "picture": user.picture.url if user.picture else "Populate with defautl image url",
                "location": user.feo.location.country.name,
                "role": "Field Executive Officer",
                "phone_number": user.phone_number.national_number,
                "access": access,
                "refresh": refresh,
            }
        
        return payload
            

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=4)


class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    class Meta:
        model = User
        fields = ["email", "new_password", "confirm_password"]

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return attrs
