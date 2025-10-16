from django.db import models

# Create your models here.

class Board(models.Model):
    title = models.CharField(max_length=100)
    members = models.ManyToManyField('auth.User', related_name='boards')
    owner = models.ForeignKey('auth.User', related_name='owned_boards', on_delete=models.CASCADE)

    def __str__(self):
        return self.title