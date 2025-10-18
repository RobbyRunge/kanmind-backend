from django.contrib.auth.models import User

from rest_framework import serializers

from user_auth_app.api.serializers import UserSerializer
from tasks_app.models import Task, Comment


class TaskListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing and displaying tasks.
    
    Includes nested user data for assignee and reviewer,
    and a calculated field for the number of comments.
    
    Used for:
    - GET /api/tasks/ (list view)
    - Task responses after create/update operations
    """
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority',
                  'assignee', 'reviewer', 'due_date', 'comments_count']

    def get_comments_count(self, obj):
        """Return the total number of comments on this task."""
        return obj.comments.count()


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new tasks.
    
    Accepts user IDs for assignee and reviewer instead of nested objects.
    Validates that assigned users are members of the task's board.
    
    The authenticated user is automatically set as created_by in the view.
    
    Used for: POST /api/tasks/
    """
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ['board', 'title', 'description', 'status', 'priority',
                  'assignee_id', 'reviewer_id', 'due_date']

    def validate(self, data):
        """
        Validate that assignee and reviewer exist and are board members.
        
        Raises ValidationError if:
        - User ID does not exist
        - User is not a member of the specified board
        """
        board = data.get('board')
        assignee_id = data.get('assignee_id')
        reviewer_id = data.get('reviewer_id')

        # Validate assignee
        if assignee_id:
            try:
                assignee = User.objects.get(id=assignee_id)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {'assignee_id': 'User does not exist.'})

            if not board.members.filter(id=assignee_id).exists():
                raise serializers.ValidationError(
                    {'assignee_id': 'User must be a member of the board.'})

        # Validate reviewer
        if reviewer_id:
            try:
                reviewer = User.objects.get(id=reviewer_id)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {'reviewer_id': 'User does not exist.'})

            if not board.members.filter(id=reviewer_id).exists():
                raise serializers.ValidationError(
                    {'reviewer_id': 'User must be a member of the board.'})

        return data

    def create(self, validated_data):
        """
        Create a new task and assign users.
        
        Extracts assignee_id and reviewer_id from validated data
        and sets them as foreign keys on the task instance.
        """
        assignee_id = validated_data.pop('assignee_id', None)
        reviewer_id = validated_data.pop('reviewer_id', None)

        task = Task.objects.create(**validated_data)

        if assignee_id:
            task.assignee_id = assignee_id
        if reviewer_id:
            task.reviewer_id = reviewer_id

        task.save()
        return task
    

class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing tasks.
    
    Allows partial updates of task fields.
    Validates that assigned users are members of the task's board.
    
    Used for: PATCH /api/tasks/{id}/
    """
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority',
                  'assignee_id', 'reviewer_id', 'due_date']
    
    def validate(self, data):
        """
        Validate that assignee and reviewer exist and are board members.
        
        Uses the existing task's board for validation.
        """
        board = self.instance.board
        assignee_id = data.get('assignee_id')
        reviewer_id = data.get('reviewer_id')
        
        # Validate assignee
        if assignee_id:
            try:
                assignee = User.objects.get(id=assignee_id)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {'assignee_id': 'User does not exist.'})

            if not board.members.filter(id=assignee_id).exists():
                raise serializers.ValidationError(
                    {'assignee_id': 'User must be a member of the board.'})

        # Validate reviewer
        if reviewer_id:
            try:
                reviewer = User.objects.get(id=reviewer_id)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {'reviewer_id': 'User does not exist.'})

            if not board.members.filter(id=reviewer_id).exists():
                raise serializers.ValidationError(
                    {'reviewer_id': 'User must be a member of the board.'})

        return data
    
    def update(self, instance, validated_data):
        """
        Update task fields and reassign users if provided.
        
        Only updates assignee/reviewer if explicitly provided in the request.
        This allows setting them to null by passing null in the request.
        """
        assignee_id = validated_data.pop('assignee_id', None)
        reviewer_id = validated_data.pop('reviewer_id', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update assignee/reviewer only if explicitly provided
        if 'assignee_id' in self.initial_data:
            instance.assignee_id = assignee_id
        if 'reviewer_id' in self.initial_data:
            instance.reviewer_id = reviewer_id
        
        instance.save()
        return instance
    

class TaskDeleteSerializer(serializers.ModelSerializer):
    """
    Serializer for task deletion operations.
    
    Used to validate task deletion requests.
    Currently has no fields as deletion requires no input data.
    """
    class Meta:
        model = Task
        fields = []


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying comments.
    
    Shows the author's full name (first + last) if available,
    otherwise falls back to the username.
    
    Used for:
    - GET /api/tasks/{task_id}/comments/ (list view)
    - Comment responses after create operations
    """
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
    
    def get_author(self, obj):
        """
        Return the author's full name or username as fallback.
        
        Format: "FirstName LastName" or "username" if names not set.
        """
        full_name = obj.author.get_full_name()
        return full_name if full_name.strip() else obj.author.username


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new comments.
    
    Only requires content in the request body.
    Task and author are set automatically in the view.
    
    Used for: POST /api/tasks/{task_id}/comments/
    """
    class Meta:
        model = Comment
        fields = ['content']
    
    def validate_content(self, value):
        """
        Validate that comment content is not empty.
        
        Raises ValidationError if content is empty or only whitespace.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value