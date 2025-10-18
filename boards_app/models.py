from django.db import models


class Board(models.Model):
    """
    Kanban Board model for organizing tasks and managing team collaboration.
    
    Each board has an owner and can have multiple members.
    Tasks are associated with boards through a foreign key relationship.
    
    Relationships:
        - owner: One user owns the board (can delete and manage)
        - members: Multiple users can be members (can view and edit tasks)
        - tasks: Multiple tasks belong to a board (reverse relation via Task.board)
    """
    title = models.CharField(max_length=100)
    members = models.ManyToManyField(
        'auth.User', 
        related_name='boards',
        help_text="Users who can access and collaborate on this board"
    )
    owner = models.ForeignKey(
        'auth.User', 
        related_name='owned_boards', 
        on_delete=models.CASCADE,
        help_text="User who created and owns this board"
    )

    def __str__(self):
        return self.title