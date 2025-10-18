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
        board_id = request.data.get('board')
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response(
                {'detail': 'Board not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not board.members.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'You must be a member of the board to create tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = serializer.save(created_by=request.user)

        response_serializer = TaskListSerializer(task)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()

        if not task.board.members.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'You must be a member of the board to update tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaskUpdateSerializer(
            task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_task = serializer.save()

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

    @action(detail=True, methods=['delete'], url_path='comments/(?P<comment_id>[^/.]+)')
    def delete_comment(self, request, pk=None, comment_id=None):
        task = self.get_object()

        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {'detail': 'Comment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if comment.task.id != task.id:
            return Response(
                {'detail': 'Comment does not belong to this task.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if comment.author != request.user:
            return Response(
                {'detail': 'Only the comment author can delete this comment.'},
                status=status.HTTP_403_FORBIDDEN
            )

        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
