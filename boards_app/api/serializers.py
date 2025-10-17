from django.contrib.auth.models import User

from rest_framework import serializers

from ..models import Board
from user_auth_app.api.serializers import UserSerializer
from tasks_app.api.serializers import TaskSerializer


class BoardListSerializer(serializers.ModelSerializer):
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
        return obj.members.count()

    def get_ticket_count(self, obj):
        # Total count aller Tasks
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        # Count der Tasks mit Status 'to-do'
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        # Count der Tasks mit Priority 'high'
        return obj.tasks.filter(priority='high').count()


class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
        read_only_fields = ['id', 'owner_id']


class BoardCreateSerializer(serializers.ModelSerializer):
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
        if value:
            existing_users = User.objects.filter(id__in=value).values_list('id', flat=True)
            invalid_ids = set(value) - set(existing_users)
            if invalid_ids:
                raise serializers.ValidationError(
                    f"Invalid user IDs: {', '.join(map(str, invalid_ids))}"
                )
        return value

    def create(self, validated_data):
        member_ids = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        
        if member_ids:
            users = User.objects.filter(id__in=member_ids)
            board.members.set(users)
        
        return board