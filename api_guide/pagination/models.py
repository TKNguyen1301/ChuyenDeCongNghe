from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Product(models.Model):
    """
    Product model for demonstrating various pagination styles.
    Includes a created timestamp for cursor pagination.
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    stock_quantity = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']  # Default ordering by creation time
        indexes = [
            models.Index(fields=['-created']),  # Index for cursor pagination
            models.Index(fields=['category']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return self.name


class Order(models.Model):
    """
    Order model for testing pagination with related fields.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    shipping_address = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['-order_date']),
            models.Index(fields=['status']),
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"


class OrderItem(models.Model):
    """
    Order item model for demonstrating pagination with nested relationships.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Article(models.Model):
    """
    Article model for demonstrating different ordering strategies.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    slug = models.SlugField(unique=True)  # Good for cursor pagination
    published = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['slug']),
            models.Index(fields=['-view_count']),
        ]

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Comment model for testing nested pagination.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']  # Ascending order for comments
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.article.title}"


class Billing(models.Model):
    """
    Billing model specifically for the documentation example.
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='billing_records')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_date = models.DateTimeField()
    description = models.CharField(max_length=200)
    paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-billing_date']
        indexes = [
            models.Index(fields=['-billing_date']),
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f"Billing {self.id} - {self.customer.username} - ${self.amount}"


class Account(models.Model):
    """
    Account model for demonstrating the API examples in the documentation.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    account_type = models.CharField(max_length=20, choices=[
        ('checking', 'Checking'),
        ('savings', 'Savings'),
        ('credit', 'Credit'),
    ])
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['account_number']),
        ]

    def __str__(self):
        return f"{self.account_number} - {self.user.username}"