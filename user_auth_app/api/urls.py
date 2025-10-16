from django.urls import path
from .views import RegistrationView, UserProfileList

urlpatterns = [
    path('profiles/', UserProfileList.as_view(), name='userprofile-list'),
    path('registration/', RegistrationView.as_view(), name='registration'),
]