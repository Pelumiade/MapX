
from .views import ChangePasswordView, ForgotPasswordAPIView, VerifyCodeAPIView, SetNewPasswordAPIView, LogoutView, LoginAPIView
from django.urls import path, include

urlpatterns = [
    path('api/change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('api/loginapi/', LoginAPIView.as_view(), name='api_login'),
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/forgot_password/', ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('api/verify_code/', VerifyCodeAPIView.as_view(), name='verify_code'),
    path('api/setnew_password/', SetNewPasswordAPIView.as_view(), name='setnew_password'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    

]
