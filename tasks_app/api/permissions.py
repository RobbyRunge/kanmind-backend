from rest_framework import permissions


class IsBoardOwner(permissions.BasePermission):
    """
    Custom permission to check if the user is the owner of the board
    that the task belongs to.
    
    This permission is used for operations that require board ownership,
    such as deleting tasks created by other users.
    
    Permission is granted if:
        - The user is the owner of the board associated with the task
    """
    def has_object_permission(self, request, view, obj):
        # obj is expected to be a Task instance
        # Check if the user owns the board that the task belongs to
        return obj.board.owner == request.user
