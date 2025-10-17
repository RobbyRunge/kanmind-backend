from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Task
from .serializers import TaskListSerializer


class TaskViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskListSerializer

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        tasks = Task.objects.filter(assignee=request.user)

        serializer = TaskListSerializer(tasks, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def reviewing(self, request):
        tasks = Task.objects.filter(reviewer=request.user)

        serializer = TaskListSerializer(tasks, many=True)

        return Response(serializer.data)
