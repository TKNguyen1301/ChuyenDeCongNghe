from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """
    Category model for products.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']


class Product(models.Model):
    """
    Product model for filtering examples.
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.JSONField(default=list, blank=True)  # For JSON field filtering examples
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_products')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Purchase(models.Model):
    """
    Purchase model for filtering examples (from DRF documentation).
    """
    purchaser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ], default='pending')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.purchaser.username} - {self.product.name}"

    class Meta:
        ordering = ['-purchase_date']


class UserProfile(models.Model):
    """
    Extended user profile for filtering examples.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='filtering_profile')
    profession = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    interests = models.JSONField(default=list, blank=True)  # For JSON field filtering

    def __str__(self):
        return f"{self.user.username}'s profile"


class Review(models.Model):
    """
    Review model for complex filtering examples.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    helpful_votes = models.PositiveIntegerField(default=0)
    verified_purchase = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.rating}/5"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'reviewer']


class Booking(models.Model):
    """
    Booking model for ordering examples.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ], default='pending')
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']