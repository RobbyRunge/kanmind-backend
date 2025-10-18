from django.contrib.auth.models import User

from rest_framework import serializers

from user_auth_app.api.serializers import UserSerializer
from tasks_app.models import Task


class TaskListSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority',
                  'assignee', 'reviewer', 'due_date', 'comments_count']

    def get_comments_count(self, obj):
        # Placeholder: wird implementiert wenn Comments vorhanden sind
        return 0


class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ['board', 'title', 'description', 'status', 'priority',
                  'assignee_id', 'reviewer_id', 'due_date']

    def validate(self, data):
        board = data.get('board')
        assignee_id = data.get('assignee_id')
        reviewer_id = data.get('reviewer_id')

        if assignee_id:
            try:
                assignee = User.objects.get(id=assignee_id)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {'assignee_id': 'User does not exist.'})

            if not board.members.filter(id=assignee_id).exists():
                raise serializers.ValidationError(
                    {'assignee_id': 'User must be a member of the board.'})

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
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority',
                  'assignee_id', 'reviewer_id', 'due_date']
    
    def validate(self, data):
        board = self.instance.board
        assignee_id = data.get('assignee_id')
        reviewer_id = data.get('reviewer_id')
        
        if assignee_id:
            try:
                assignee = User.objects.get(id=assignee_id)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {'assignee_id': 'User does not exist.'})

            if not board.members.filter(id=assignee_id).exists():
                raise serializers.ValidationError(
                    {'assignee_id': 'User must be a member of the board.'})

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
        assignee_id = validated_data.pop('assignee_id', None)
        reviewer_id = validated_data.pop('reviewer_id', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if 'assignee_id' in self.initial_data:
            instance.assignee_id = assignee_id
        if 'reviewer_id' in self.initial_data:
            instance.reviewer_id = reviewer_id
        
        instance.save()
        return instance
    
class TaskDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = []