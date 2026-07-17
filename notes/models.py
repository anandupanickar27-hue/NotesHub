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
    is_seed = models.BooleanField(default=False)
    def __str__(self):
        return self.title
    
class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    bio = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.user.username
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):

    if created:

        Profile.objects.create(
            user=instance
        )


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):

    instance.profile.save()