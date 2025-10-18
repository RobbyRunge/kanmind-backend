from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Task, Comment
from .serializers import (
    TaskListSerializer, 
    TaskCreateSerializer, 
    TaskUpdateSerializer, 
    CommentSerializer,
    CommentCreateSerializer
)
from .permissions import IsBoardOwner
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
        
        # Task erstellen - created_by automatisch setzen
        task = serializer.save(created_by=request.user)
        
        response_serializer = TaskListSerializer(task)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        # Task holen (404 wenn nicht gefunden)
        task = self.get_object()
        
        # Permission: User muss Board-Member sein
        if not task.board.members.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'You must be a member of the board to update tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update mit TaskUpdateSerializer
        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_task = serializer.save()
        
        # Response mit nested User-Objekten
        response_serializer = TaskListSerializer(updated_task)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        
        is_creator = task.created_by == request.user
        is_board_owner = task.board.owner == request.user
        
        if not (is_creator or is_board_owner):
            return Response(
                {'detail': 'Only the task creator or board owner can delete tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def comments(self, request, pk=None):
        task = self.get_object()
        
        if not task.board.members.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'You must be a member of the board to access comments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.method == 'GET':
            comments = task.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            serializer = CommentCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            comment = serializer.save(
                task=task,
                author=request.user
            )
            
            response_serializer = CommentSerializer(comment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
