from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    done = models.TextField(default='❌')

    def __str__(self):
        return self.title
