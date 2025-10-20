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
    """
    ViewSet for managing tasks and their comments.
    
    Provides endpoints for:
    - Creating, updating, and deleting tasks
    - Filtering tasks by assignee or reviewer
    - Managing task comments (create, list, delete)
    
    All endpoints require authentication and appropriate permissions.
    
    Main Endpoints:
    - POST /api/tasks/ - Create a new task
    - PATCH /api/tasks/{id}/ - Update a task
    - DELETE /api/tasks/{id}/ - Delete a task
    - GET /api/tasks/assigned-to-me/ - Get tasks assigned to current user
    - GET /api/tasks/reviewing/ - Get tasks user is reviewing
    - GET /api/tasks/{id}/comments/ - Get all comments on a task
    - POST /api/tasks/{id}/comments/ - Add a comment to a task
    - DELETE /api/tasks/{id}/comments/{comment_id}/ - Delete a comment
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskListSerializer

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        """
        Get all tasks assigned to the current user.
        
        Returns a list of tasks where the user is set as the assignee.
        Useful for "My Tasks" views in the frontend.
        
        Returns:
            200: List of assigned tasks
        """
        tasks = Task.objects.filter(assignee=request.user)
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def reviewing(self, request):
        """
        Get all tasks where the current user is the reviewer.
        
        Returns a list of tasks where the user is set as the reviewer.
        Useful for "Review Queue" views in the frontend.
        
        Returns:
            200: List of tasks to review
        """
        tasks = Task.objects.filter(reviewer=request.user)
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a new task on a board.
        
        The authenticated user is automatically set as the task creator.
        Only board members can create tasks on that board.
        
        Validates:
        - Board exists
        - User is a board member
        - Assignee and reviewer (if provided) are board members
        
        Returns:
            201: Task created successfully
            400: Invalid input data
            403: User is not a board member
            404: Board not found
        """
        board_id = request.data.get('board')
        
        # Validate board exists
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response(
                {'detail': 'Board not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate user is board member
        if not board.members.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'You must be a member of the board to create tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate and create task
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save(created_by=request.user)

        # Return task with nested user data
        response_serializer = TaskListSerializer(task)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        """
        Update specific fields of a task.
        
        Allows partial updates without requiring all fields.
        Only board members can update tasks.
        
        Validates:
        - User is a board member
        - Assignee and reviewer (if changed) are board members
        
        Returns:
            200: Task updated successfully
            400: Invalid input data
            403: User is not a board member
            404: Task not found
        """
        task = self.get_object()

        # Validate user is board member
        if not task.board.members.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'You must be a member of the board to update tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate and update task
        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_task = serializer.save()

        # Return updated task with nested user data
        response_serializer = TaskListSerializer(updated_task)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a task.
        
        Only the task creator or the board owner can delete tasks.
        This prevents users from deleting other members' tasks.
        
        Permissions:
        - Task creator: Can delete their own tasks
        - Board owner: Can delete any task on their board
        
        Returns:
            204: Task deleted successfully
            403: User does not have permission to delete
            404: Task not found
        """
        task = self.get_object()

        is_creator = task.created_by == request.user
        is_board_owner = task.board.owner == request.user

        # Check if user has permission to delete
        if not (is_creator or is_board_owner):
            return Response(
                {'detail': 'Only the task creator or board owner can delete tasks.'},
                status=status.HTTP_403_FORBIDDEN
            )

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def comments(self, request, pk=None):
        """
        Handle comment operations on a task.
        
        GET: Retrieve all comments for a task (chronologically ordered)
        POST: Add a new comment to a task
        
        The author is automatically set to the authenticated user.
        Only board members can view and add comments.
        
        Returns:
            GET 200: List of comments
            POST 201: Comment created successfully
            POST 400: Invalid comment data
            403: User is not a board member
            404: Task not found
        """
        task = self.get_object()

        # Validate user is board member
        if not task.board.members.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'You must be a member of the board to access comments.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # GET: List all comments
        if request.method == 'GET':
            comments = task.comments.all()  # Already ordered by created_at
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # POST: Create new comment
        elif request.method == 'POST':
            serializer = CommentCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Save comment with automatic task and author assignment
            comment = serializer.save(
                task=task,
                author=request.user
            )

            # Return comment with formatted author name
            response_serializer = CommentSerializer(comment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='comments/(?P<comment_id>[^/.]+)')
    def delete_comment(self, request, pk=None, comment_id=None):
        """
        Delete a specific comment from a task.
        
        Only the comment author can delete their own comments.
        Uses a nested URL pattern to specify both task and comment IDs.
        
        URL Pattern: /api/tasks/{task_id}/comments/{comment_id}/
        
        Validates:
        - Task exists
        - Comment exists
        - Comment belongs to the specified task
        - User is the comment author
        
        Returns:
            204: Comment deleted successfully
            403: User is not the comment author
            404: Task or comment not found or doesn't belong to task
        """
        # Validate task exists first (without permission check)
        try:
            task = Task.objects.get(id=pk)
        except Task.DoesNotExist:
            return Response(
                {'detail': 'Task not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate comment exists
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {'detail': 'Comment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate comment belongs to this task
        if comment.task.id != task.id:
            return Response(
                {'detail': 'Comment does not belong to this task.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate user is the comment author
        if comment.author != request.user:
            return Response(
                {'detail': 'Only the comment author can delete this comment.'},
                status=status.HTTP_403_FORBIDDEN
            )

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
