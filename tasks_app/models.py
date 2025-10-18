from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    """
    Task model representing individual work items within a Kanban board.
    
    Tasks can be assigned to users, have priority levels, due dates,
    and move through different workflow statuses.
    
    Status Flow:
        to-do → in-progress → review → done
    
    Relationships:
        - board: Task belongs to one board
        - assignee: User responsible for completing the task (optional)
        - reviewer: User responsible for reviewing the task (optional)
        - created_by: User who created the task
        - comments: Multiple comments can be added to a task (reverse relation)
    
    Deletion behavior:
        - If board is deleted: Task is deleted (CASCADE)
        - If assignee/reviewer is deleted: Field is set to NULL (SET_NULL)
        - If creator is deleted: Task is deleted (CASCADE)
    """
    STATUS_CHOICES = [
        ('to-do', 'To Do'),
        ('in-progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    board = models.ForeignKey(
        'boards_app.Board',
        related_name='tasks',
        on_delete=models.CASCADE,
        help_text="Board this task belongs to"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='to-do',
        help_text="Current workflow status of the task"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level of the task"
    )
    assignee = models.ForeignKey(
        User,
        related_name='assigned_tasks',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User responsible for completing this task"
    )
    reviewer = models.ForeignKey(
        User,
        related_name='reviewed_tasks',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User responsible for reviewing this task"
    )
    created_by = models.ForeignKey(
        User,
        related_name='created_tasks',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="User who created this task"
    )
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Comment model for task discussions and updates.
    
    Comments allow users to communicate about tasks, ask questions,
    provide updates, or share information.
    
    Relationships:
        - task: Comment belongs to one task
        - author: User who wrote the comment
    
    Ordering:
        Comments are ordered chronologically by creation date.
    
    Deletion behavior:
        - If task is deleted: Comment is deleted (CASCADE)
        - If author is deleted: Comment is deleted (CASCADE)
    """
    task = models.ForeignKey(
        Task,
        related_name='comments',
        on_delete=models.CASCADE,
        help_text="Task this comment is associated with"
    )
    author = models.ForeignKey(
        User,
        related_name='task_comments',
        on_delete=models.CASCADE,
        help_text="User who wrote this comment"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']  # Chronological order

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"
