from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileListView, RegistrationView, LoginView

router = DefaultRouter()
router.register(r'profiles', UserProfileListView, basename='userprofile')

urlpatterns = [
    path('', include(router.urls)),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
]