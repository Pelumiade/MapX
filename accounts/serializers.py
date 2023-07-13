from rest_framework import serializers
from django.contrib.auth.models import User

from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = User.objects.filter(email=email).get()

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
                "location": user.location,
                "role": "Admin",
                "phone_number": user.phone_number.national_number,
            }
        else:
            payload = {
                "email": email,
                "first_name": user.feo.first_name,
                "last_name": user.feo.last_name,
                "designation": "Field Executive Officer",
                "picture": user.feo.picture.url if user.feo.picture else "lol",
                "location": user.feo.location,
                "role": "Field Executive Officer",
                "phone_number": user.feo.phone_number,
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
    confirm_new_password = serializers.CharField()