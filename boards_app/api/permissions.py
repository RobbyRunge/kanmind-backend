from rest_framework import permissions

class IsBoardMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user in obj.members.all()