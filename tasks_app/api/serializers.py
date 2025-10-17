from rest_framework import serializers

from user_auth_app.api.serializers import UserSerializer
from tasks_app.models import Task


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 
                  'assignee', 'reviewer', 'due_date', 'comments_count']
    
    def get_comments_count(self, obj):
        # Placeholder: wird implementiert wenn Comments vorhanden sind
        return 0