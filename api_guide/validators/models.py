from django.db import models
from django.utils import timezone


class CustomerReportRecord(models.Model):
    """
    Example model from Django REST Framework validators documentation.
    Demonstrates basic uniqueness constraint validation.
    """
    time_raised = models.DateTimeField(default=timezone.now, editable=False)
    reference = models.CharField(unique=True, max_length=20)
    description = models.TextField()

    def __str__(self):
        return f"Report {self.reference} - {self.time_raised}"

    class Meta:
        ordering = ['-time_raised']


class BlogPost(models.Model):
    """
    Example model for demonstrating UniqueValidator and date-based validators.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100)
    content = models.TextField()
    published = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='blog_posts')
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published']


class ToDoList(models.Model):
    """
    Parent model for ToDo items to demonstrate UniqueTogetherValidator.
    """
    name = models.CharField(max_length=100)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='todo_lists')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ToDoItem(models.Model):
    """
    Model to demonstrate UniqueTogetherValidator for list + position uniqueness.
    """
    list = models.ForeignKey(ToDoList, on_delete=models.CASCADE, related_name='items')
    position = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} (pos: {self.position})"

    class Meta:
        ordering = ['position']


class BillingRecord(models.Model):
    """
    Model to demonstrate handling of optional fields in validators.
    """
    client = models.CharField(max_length=100, blank=True)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Billing for {self.client or 'Unknown'} - ${self.amount}"

    class Meta:
        ordering = ['-date']
