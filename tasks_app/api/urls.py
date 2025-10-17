from django.urls import include, path


urlpatterns = [
    path('/api/tasks/assigned-to-me/'),
    path('/api/tasks/reviewing/'),
]
