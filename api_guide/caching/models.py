from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Post(models.Model):
    """
    Simple Post model for caching examples.
    """
    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class UserProfile(models.Model):
    """
    User profile model for caching examples.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class UserFeed(models.Model):
    """
    User feed model to simulate user-specific content.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feed_items')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    feed_type = models.CharField(max_length=50, choices=[
        ('news', 'News'),
        ('updates', 'Updates'),
        ('notifications', 'Notifications'),
    ], default='news')

    def __str__(self):
        return f"Feed for {self.user.username} - {self.feed_type}"

    class Meta:
        ordering = ['-created_at']