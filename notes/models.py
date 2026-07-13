from django.db import models
from django.contrib.auth.models import User



class Category(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    summary = models.TextField(blank=True)
    tags = models.CharField(max_length=255, blank=True)
    ai_generated = models.BooleanField(default=False)
    embedding_status = models.BooleanField(default=False)
    def __str__(self):
        return self.title