from django.contrib.auth.models import User

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
    permission_classes = [permissions.IsAuthenticated]
    queryset = Board.objects.all()

    def get_queryset(self):
        return self.queryset.filter(members=self.request.user)

    def get_serializer_class(self):
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
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsBoardMember]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save(owner=request.user)

        if not board.members.filter(id=request.user.id).exists():
            board.members.add(request.user)

        response_serializer = BoardListSerializer(board)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        response_serializer = BoardUpdateResponseSerializer(board)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        response_serializer = BoardUpdateResponseSerializer(board)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if not self.get_object():
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif not self.get_object().members.filter(id=request.user.id).exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        elif self.get_object().owner != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailCheckAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {'email': ['This field is required.']},
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
