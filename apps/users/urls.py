from django.urls import path
from apps.users.views import (
    RegisterView,
    UserProfileView,
    ChangePasswordView,
    RequestResetPasswordView,
    ConfirmResetPasswordView,
)
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('request-reset-password/', RequestResetPasswordView.as_view(), name='request-reset-password'),
    path('confirm-reset-password/', ConfirmResetPasswordView.as_view(), name='confirm-reset-password'),

    # jwt
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
