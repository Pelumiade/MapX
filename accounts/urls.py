
from .views import ChangePasswordView, ForgotPasswordAPIView, VerifyCodeAPIView, SetNewPasswordAPIView, LogoutView, LoginAPIView
from django.urls import path

urlpatterns = [
    path('api/change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('api/loginapi/', LoginAPIView.as_view(), name='api_login'),
    path('api/forgot_password/', ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('api/verify_code/', VerifyCodeAPIView.as_view(), name='verify_code'),
    path('api/reset_password/', SetNewPasswordAPIView.as_view(), name='reset_password'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    

]
