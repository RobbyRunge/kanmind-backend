from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Task
from .serializers import TaskListSerializer, TaskCreateSerializer
from boards_app.models import Board


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
    
    def create(self, request, *args, **kwargs):
        # Prüfen ob Board existiert (404 wenn nicht)
        board_id = request.data.get('board')
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response(
                {'detail': 'Board not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prüfen ob User Member des Boards ist (403 wenn nicht)
        if not board.members.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'You must be a member of the board to create tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Input: TaskCreateSerializer validiert assignee, reviewer
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Task erstellen
        task = serializer.save()
        
        response_serializer = TaskListSerializer(task)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
