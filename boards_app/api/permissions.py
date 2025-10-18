from rest_framework import permissions


class IsBoardMember(permissions.BasePermission):
    """
    Custom permission to only allow board owners and members to access the board.
    
    Users are granted access if they are either:
    - The owner of the board
    - A member of the board
    
    This permission is used to restrict board detail views, updates, and deletions.
    """
    def has_object_permission(self, request, view, obj):
        # Owner always has permission
        # Members also have permission to view and edit
        return obj.owner == request.user or request.user in obj.members.all()