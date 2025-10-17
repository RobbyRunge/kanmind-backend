from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet  # Was importieren?

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')  # Ausfüllen!

urlpatterns = [
    path('', include(router.urls)),
]