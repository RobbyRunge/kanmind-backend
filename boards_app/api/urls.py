from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BoardViewSet, EmailCheckAPIView

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')

urlpatterns = [
    path('', include(router.urls)),
    path('email-check/', EmailCheckAPIView.as_view(), name='email-check'),
]