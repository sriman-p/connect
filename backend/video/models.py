from django.db import models
from users.models import User

class Placeholder(models.Model):
    """Placeholder model"""
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
