from django.urls import path
from .views import (
    LoginView, RefreshTokenView, MeView, UserMenusView, ChangePasswordView
)

app_name = 'auth'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshTokenView.as_view(), name='token-refresh'),
    path('me/', MeView.as_view(), name='me'),
    path('menus/', UserMenusView.as_view(), name='user-menus'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
