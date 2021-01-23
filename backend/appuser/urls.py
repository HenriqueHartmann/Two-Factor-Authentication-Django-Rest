from django.urls import path
from knox.views import LogoutView

from .views import UserAPIView, RegisterAPIView, LoginAPIView, VerifyEmail

urlpatterns = [
    path('user/', UserAPIView.as_view(), name='get-user'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('email-verify/', VerifyEmail.as_view(), name='email-verify'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='knox_logout')
]
