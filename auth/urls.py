from django.urls import path
from .views import (
    UserRegistrationView,
    LoginView,
    LogoutView,
    ProfileView,
    DeleteAccountView
)

app_name = 'auth'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('account/', DeleteAccountView.as_view(), name='delete_account'),
]
