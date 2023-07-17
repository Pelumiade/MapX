# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import GenericAPIView

from accounts.models import User
from .serializers import (
    ForgotPasswordSerializer, SetNewPasswordSerializer,
    VerifyCodeSerializer, LoginSerializer, ChangePasswordSerializer
)
from .tasks import send_email
import random


class CustomObtainAuthToken(ObtainAuthToken):
   
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    

class ForgotPasswordAPIView(GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    authentication_classes = ()
    permission_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            print(email)
            try:
                user = User.objects.filter(email=email).get()
            except User.DoesNotExist:
                return Response({"error": "Invalid email address. Enter a correct email address"}, status=status.HTTP_400_BAD_REQUEST)

            otp = str(random.randint(1000, 9999))
            print(otp)
            user.verification_code = otp
            user.save(update_fields=["verification_code"])
            # send email
            subject = "Password Reset Verification code"
            body = f'Your verification code is {otp}'
            data = {"email_body": body, "to_email": email,
                    "email_subject": subject}
            send_email(data)
            return Response({'message': 'Verification code sent successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyCodeAPIView(GenericAPIView):
    serializer_class = VerifyCodeSerializer
    authentication_classes = ()
    permission_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        verification_code = serializer.validated_data["verification_code"]
        try:
            user = User.objects.filter(email=email).get()
        except User.DoesNotExist:
            return Response({"message": "Incorrect credential"}, status=status.HTTP_404_NOT_FOUND)
        print(user.verification_code)
        if user.verification_code != verification_code:
            return Response({"message": "Incorrect verification pin."}, status=status.HTTP_400_BAD_REQUEST)
        user.verification_code = ""
        user.save(update_fields=["verification_code"])
        return Response({"message": "verification successful"}, status=status.HTTP_200_OK)


class SetNewPasswordAPIView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    authentication_classes = ()
    permission_classes = []

    def post(self, request):
        serilizer = self.get_serializer(data=request.data)
        serilizer.is_valid(raise_exception=True)
        email = serilizer.validated_data["email"]
        new_password = serilizer.validated_data["new_password"]
        user = User.objects.filter(email=email).get()
        if user:
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid email address"}, status=status.HTTP_400_BAD_REQUEST)
    
    
class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class LogoutView(GenericAPIView):

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

