from django.urls import path
from .views import UserProfileListView, UserProfileDetailView, RegistrationView, LoginView

urlpatterns = [
    path('profiles/', UserProfileListView.as_view(), name='userprofile-list'),
    path('profiles/<int:pk>/', UserProfileDetailView.as_view(), name='userprofile-detail'),

    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
]