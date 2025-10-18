from django.contrib.auth.models import User

from rest_framework import serializers

from ..models import Board
from user_auth_app.api.serializers import UserSerializer
from tasks_app.api.serializers import TaskListSerializer


class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing boards with summary statistics.
    
    Provides an overview with calculated fields:
    - member_count: Number of board members
    - ticket_count: Total number of tasks on the board
    - tasks_to_do_count: Number of tasks with 'to-do' status
    - tasks_high_prio_count: Number of high-priority tasks
    
    Used for: GET /api/boards/ (list view)
    """
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']
        read_only_fields = ['id', 'owner_id']

    def get_member_count(self, obj):
        """Return the total number of board members."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the total number of tasks on this board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks with 'to-do' status."""
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of high-priority tasks."""
        return obj.tasks.filter(priority='high').count()


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed board view with nested members and tasks.
    
    Includes full nested representations of:
    - members: All users who are board members
    - tasks: All tasks associated with the board
    
    Used for: GET /api/boards/{id}/ (detail view)
    """
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
        read_only_fields = ['id', 'owner_id']


class BoardCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new boards.
    
    Accepts:
    - title: Board name (required)
    - members: List of user IDs to add as members (optional)
    
    The authenticated user is automatically set as the owner.
    The owner is also automatically added to the members list if not present.
    
    Used for: POST /api/boards/
    """
    members = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Board
        fields = ['title', 'members']

    def validate_members(self, value):
        """
        Validate that all provided user IDs exist in the database.
        
        Raises ValidationError if any user ID is invalid.
        """
        if value:
            existing_users = User.objects.filter(id__in=value).values_list('id', flat=True)
            invalid_ids = set(value) - set(existing_users)
            if invalid_ids:
                raise serializers.ValidationError(
                    f"Invalid user IDs: {', '.join(map(str, invalid_ids))}"
                )
        return value

    def create(self, validated_data):
        """
        Create a new board and assign members.
        
        The owner is automatically set in the view.
        """
        member_ids = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        
        if member_ids:
            users = User.objects.filter(id__in=member_ids)
            board.members.set(users)
        
        return board
    

class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing boards.
    
    Allows updating:
    - title: Board name
    - members: List of user IDs (replaces existing members)
    
    Used for: PUT/PATCH /api/boards/{id}/
    """
    members = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Board
        fields = ['title', 'members']

    def validate_members(self, value):
        """
        Validate that all provided user IDs exist in the database.
        
        Raises ValidationError if any user ID is invalid.
        """
        if value:
            existing_users = User.objects.filter(id__in=value).values_list('id', flat=True)
            invalid_ids = set(value) - set(existing_users)
            if invalid_ids:
                raise serializers.ValidationError(
                    f"Invalid user IDs: {', '.join(map(str, invalid_ids))}"
                )
        return value

    def update(self, instance, validated_data):
        """
        Update board fields and replace member list if provided.
        
        If members list is provided, it replaces all existing members.
        If members list is empty or not provided, members remain unchanged.
        """
        member_ids = validated_data.pop('members', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update members if provided
        if member_ids is not None and len(member_ids) > 0:
            users = User.objects.filter(id__in=member_ids)
            instance.members.set(users)
        
        return instance


class BoardUpdateResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for board update responses.
    
    Returns the updated board with nested user data for owner and members.
    Provides a complete view of the board after update operations.
    """
    owner_data = UserSerializer(source='owner', read_only=True)
    members_data = UserSerializer(source='members', many=True, read_only=True)
    
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']
        read_only_fields = ['id', 'owner_data', 'members_data']


class BoardDeleteSerializer(serializers.ModelSerializer):
    """
    Serializer for board deletion operations.
    
    Used to validate board deletion requests.
    Returns minimal board information in responses.
    """
    class Meta:
        model = Board
        fields = ['id', 'title']
        read_only_fields = ['id', 'title']