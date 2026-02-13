"""
Django Templates Practice Models
Following Django 5.2 documentation examples.
"""
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator
import datetime


class Category(models.Model):
    """Category model for organizing content."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('templates_practice:category_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    """Tag model for content tagging."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#007bff')  # Bootstrap blue

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('templates_practice:tag_detail', kwargs={'slug': self.slug})


class Author(models.Model):
    """Author model extending User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.URLField(blank=True, default='https://via.placeholder.com/150')
    social_media = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    def get_absolute_url(self):
        return reverse('templates_practice:author_detail', kwargs={'pk': self.pk})

    @property
    def age(self):
        """Calculate age from birth_date."""
        if self.birth_date:
            today = datetime.date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    @property
    def full_name(self):
        """Get full name or username."""
        return self.user.get_full_name() or self.user.username


class Post(models.Model):
    """Main content model demonstrating template features."""
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'
    
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
        (ARCHIVED, 'Archived'),
    ]

    title = models.CharField(max_length=200, validators=[MinLengthValidator(5)])
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField(validators=[MinLengthValidator(100)])
    excerpt = models.TextField(max_length=300, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    featured = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    view_count = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=1)  # minutes
    
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        get_latest_by = 'published_at'
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['featured', 'status']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('templates_practice:post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if self.status == self.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        
        # Auto-generate excerpt if not provided
        if not self.excerpt and self.content:
            words = self.content.split()[:50]
            self.excerpt = ' '.join(words) + '...' if len(self.content.split()) > 50 else self.content
        
        # Calculate reading time (average 200 words per minute)
        if self.content:
            word_count = len(self.content.split())
            self.reading_time = max(1, word_count // 200)
        
        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return self.status == self.PUBLISHED and self.published_at

    @property
    def days_since_published(self):
        if self.published_at:
            return (timezone.now() - self.published_at).days
        return None

    @property
    def word_count(self):
        return len(self.content.split()) if self.content else 0

    def get_related_posts(self, limit=3):
        """Get related posts by category and tags."""
        related = Post.objects.filter(
            status=self.PUBLISHED,
            category=self.category
        ).exclude(pk=self.pk)
        
        if related.count() < limit:
            # Get more posts by tags
            tag_related = Post.objects.filter(
                status=self.PUBLISHED,
                tags__in=self.tags.all()
            ).exclude(pk=self.pk).distinct()
            
            related = (related | tag_related).distinct()
        
        return related[:limit]


class Comment(models.Model):
    """Comment model for posts."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    author_website = models.URLField(blank=True)
    content = models.TextField(validators=[MinLengthValidator(10), MaxLengthValidator(1000)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_approved = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author_name} on {self.post.title}'

    @property
    def is_reply(self):
        return self.parent is not None

    def get_replies(self):
        return self.replies.filter(is_approved=True, is_spam=False)


class Newsletter(models.Model):
    """Newsletter subscription model."""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    preferences = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name or 'Anonymous'} ({self.email})"


class TemplateExample(models.Model):
    """Model for demonstrating template features."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    demo_data = models.JSONField(default=dict)
    template_code = models.TextField()
    expected_output = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
