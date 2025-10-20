from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Board
from .serializers import (
    BoardListSerializer,
    BoardDetailSerializer,
    BoardCreateSerializer,
    BoardUpdateSerializer,
    BoardUpdateResponseSerializer,
    BoardDeleteSerializer
)
from .permissions import IsBoardMember


class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Kanban boards.
    
    Provides CRUD operations for boards with automatic permission handling.
    Users can only see and interact with boards they are members of.
    
    Endpoints:
    - GET /api/boards/ - List all boards where user is a member
    - POST /api/boards/ - Create a new board
    - GET /api/boards/{id}/ - Get detailed board information
    - PUT/PATCH /api/boards/{id}/ - Update board (members only)
    - DELETE /api/boards/{id}/ - Delete board (owner only)
    
    Permissions:
    - All endpoints require authentication
    - Create: Any authenticated user
    - Other operations: Board members only
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Board.objects.all()

    def get_queryset(self):
        """
        Return all boards for permission checking.
        
        We don't filter here because we want to return 403 (Forbidden)
        instead of 404 (Not Found) when a user tries to access a board
        they are not a member of.
        """
        if self.action == 'list':
            # Only for list view, filter to show user's boards
            return self.queryset.filter(members=self.request.user)
        # For detail views, return all boards to allow proper permission checking
        return self.queryset.all()

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action.
        
        Different serializers are used for different operations to control
        input/output fields and validation logic.
        """
        if self.action == 'create':
            return BoardCreateSerializer
        elif self.action == 'retrieve':
            return BoardDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return BoardUpdateSerializer
        elif self.action == 'destroy':
            return BoardDeleteSerializer
        return BoardListSerializer

    def get_permissions(self):
        """
        Dynamically assign permissions based on the action.
        
        Create action only requires authentication.
        All other actions require both authentication and board membership.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsBoardMember]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Create a new board.
        
        The authenticated user is automatically set as the owner.
        The owner is also automatically added to the members list.
        
        Returns:
            201: Board created successfully
            400: Invalid input data
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save(owner=request.user)

        # Ensure the owner is always a member
        if not board.members.filter(id=request.user.id).exists():
            board.members.add(request.user)

        response_serializer = BoardListSerializer(board)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update a board (full update).
        
        Allows updating title and members list.
        Only board members can update the board.
        
        Returns:
            200: Board updated successfully
            400: Invalid input data
            403: User is not a board member
            404: Board not found
        """
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        response_serializer = BoardUpdateResponseSerializer(board)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """
        Update a board (partial update).
        
        Allows updating individual fields without providing all required fields.
        Only board members can update the board.
        
        Returns:
            200: Board updated successfully
            400: Invalid input data
            403: User is not a board member
            404: Board not found
        """
        instance = self.get_object()

        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        response_serializer = BoardUpdateResponseSerializer(board)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a board.
        
        Only the board owner can delete the board.
        All associated tasks and data will be deleted (CASCADE).
        
        Returns:
            204: Board deleted successfully
            403: User is not the board owner
            404: Board not found
        """
        instance = self.get_object()
        
        # Check if user is the owner
        if instance.owner != request.user:
            return Response(
                {'detail': 'Only the board owner can delete this board.'},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailCheckAPIView(APIView):
    """
    API endpoint to check if a user exists by email and retrieve basic info.

    Used for adding members to boards by searching for users via email.
    Returns the user's ID, email, and full name if found.

    GET /api/email-check/?email=user@example.com

    Returns:
        200: User found - returns user data
        400: Email field missing or invalid format
        401: Not authenticated
        404: User with this email does not exist
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Look up a user by email address provided as query parameter.
        Example: GET /api/email-check/?email=user@example.com
        """
        email = request.query_params.get('email')

        if not email:
            return Response(
                {'email': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {'email': ['Invalid email address.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'email': ["This email address does not exist."]},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'id':       user.id,
            'email':    user.email,
            'fullname': user.get_full_name() or user.username
        }, status=status.HTTP_200_OK)
