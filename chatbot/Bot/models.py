from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_bot = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    page = models.IntegerField(default=1)  # New field to track the page number

    def __str__(self):
        return f"{'Bot' if self.is_bot else 'User'}: {self.message[:20]}"
