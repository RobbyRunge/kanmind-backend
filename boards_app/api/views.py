from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from ..models import Board
from .serializers import BoardListSerializer, BoardDetailSerializer, BoardCreateSerializer
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