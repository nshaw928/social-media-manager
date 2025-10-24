from django.urls import path

from .views import get_notes, logout, is_authenticated, register, verify_email_token, CustomTokenObtainPairView, CustomRefreshToken

urlpatterns = [
    path('token', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', CustomRefreshToken.as_view(), name='token_refresh'),
    path('notes', get_notes),
    path('logout', logout),
    path('authenicated', is_authenticated),
    path('register', register),
    path('verify-email/<uidb64>/<token>/', verify_email_token, name='verify_email'),
]