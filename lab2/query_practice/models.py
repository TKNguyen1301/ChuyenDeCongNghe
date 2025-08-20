"""
Django Database Queries Practice Models
Following https://docs.djangoproject.com/en/5.2/topics/db/queries/

This module demonstrates all important database query concepts in Django.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid


# ==================================================================
# 1. Blog Models (From Official Documentation)
# ==================================================================

class Blog(models.Model):
    """Blog model following the official Django documentation example."""
    name = models.CharField(max_length=100)
    tagline = models.TextField()
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Author(models.Model):
    """Author model for many-to-many relationships."""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Entry(models.Model):
    """Entry model demonstrating various field types and relationships."""
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    headline = models.CharField(max_length=255)
    body_text = models.TextField()
    pub_date = models.DateField()
    mod_date = models.DateField(default=timezone.now)
    authors = models.ManyToManyField(Author)
    number_of_comments = models.IntegerField(default=0)
    number_of_pingbacks = models.IntegerField(default=0)
    rating = models.IntegerField(default=5)
    
    def __str__(self):
        return self.headline
    
    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = "entries"


class EntryDetail(models.Model):
    """One-to-one relationship example."""
    entry = models.OneToOneField(Entry, on_delete=models.CASCADE)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Details for {self.entry.headline}"


# ==================================================================
# 2. E-commerce Models for Complex Queries
# ==================================================================

class Category(models.Model):
    """Product category with hierarchy."""
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']


class Manufacturer(models.Model):
    """Product manufacturer."""
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    founded_year = models.IntegerField()
    website = models.URLField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Product(models.Model):
    """Product model for complex query demonstrations."""
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('Tag', blank=True)
    
    # JSON field for additional attributes
    specifications = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return self.name
    
    @property
    def profit_margin(self):
        if self.cost > 0:
            return ((self.price - self.cost) / self.cost) * 100
        return 0
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['price']),
            models.Index(fields=['category', 'manufacturer']),
            models.Index(fields=['-created_at']),
        ]


class Tag(models.Model):
    """Tags for products."""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#000000')  # Hex color
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


# ==================================================================
# 3. Customer and Order Models
# ==================================================================

class Customer(models.Model):
    """Customer model."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    loyalty_points = models.PositiveIntegerField(default=0)
    is_premium = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"
    
    class Meta:
        ordering = ['user__username']


class Address(models.Model):
    """Customer address."""
    ADDRESS_TYPES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='home')
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Vietnam')
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.customer.user.username} - {self.type} - {self.city}"
    
    class Meta:
        verbose_name_plural = "addresses"


class Order(models.Model):
    """Order model."""
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    shipping_address = models.ForeignKey(Address, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    ship_date = models.DateTimeField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    @property
    def final_amount(self):
        return self.total_amount - self.discount_amount + self.tax_amount
    
    class Meta:
        ordering = ['-order_date']


class OrderItem(models.Model):
    """Order items."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def subtotal(self):
        return self.quantity * self.unit_price
    
    @property
    def discount_amount(self):
        return self.subtotal * (self.discount_percent / 100)
    
    @property
    def final_amount(self):
        return self.subtotal - self.discount_amount
    
    class Meta:
        unique_together = ['order', 'product']


# ==================================================================
# 4. Review and Rating Models
# ==================================================================

class Review(models.Model):
    """Product reviews."""
    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    helpful_votes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.rating}⭐ by {self.customer.user.username}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'customer']


# ==================================================================
# 5. Analytics and Metrics Models
# ==================================================================

class ProductView(models.Model):
    """Track product views."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    viewed_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.product.name} viewed at {self.viewed_at}"
    
    class Meta:
        ordering = ['-viewed_at']


class SalesMetrics(models.Model):
    """Daily sales metrics."""
    date = models.DateField(unique=True)
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_items_sold = models.PositiveIntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    new_customers = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Sales for {self.date}"
    
    class Meta:
        ordering = ['-date']


# ==================================================================
# 6. Inventory and Warehouse Models
# ==================================================================

class Warehouse(models.Model):
    """Warehouse locations."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    address = models.TextField()
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        ordering = ['name']


class Inventory(models.Model):
    """Product inventory by warehouse."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} at {self.warehouse.name}: {self.quantity}"
    
    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity
    
    class Meta:
        unique_together = ['product', 'warehouse']
        verbose_name_plural = "inventories"


# ==================================================================
# 7. Promotion and Discount Models
# ==================================================================

class Promotion(models.Model):
    """Marketing promotions."""
    PROMOTION_TYPES = [
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Amount Discount'),
        ('bogo', 'Buy One Get One'),
        ('free_shipping', 'Free Shipping'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=PROMOTION_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    current_uses = models.PositiveIntegerField(default=0)
    
    # Which products/categories this applies to
    products = models.ManyToManyField(Product, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    
    def __str__(self):
        return self.name
    
    @property
    def is_valid(self):
        now = timezone.now()
        return (self.is_active and 
                self.start_date <= now <= self.end_date and
                (self.max_uses is None or self.current_uses < self.max_uses))
    
    class Meta:
        ordering = ['-start_date']


# ==================================================================
# 8. Advanced Features Models
# ==================================================================

class WishList(models.Model):
    """Customer wishlist."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='My Wishlist')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.customer.user.username}'s {self.name}"
    
    class Meta:
        ordering = ['-created_at']


class WishListItem(models.Model):
    """Items in wishlist."""
    wishlist = models.ForeignKey(WishList, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.product.name} in {self.wishlist.name}"
    
    class Meta:
        unique_together = ['wishlist', 'product']
        ordering = ['-added_at']


class ProductBundle(models.Model):
    """Product bundles for cross-selling."""
    name = models.CharField(max_length=200)
    description = models.TextField()
    products = models.ManyToManyField(Product, through='BundleItem')
    bundle_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def individual_total(self):
        """Total price if buying products individually."""
        return sum(item.product.price * item.quantity for item in self.bundleitems.all())
    
    @property
    def savings(self):
        """How much customer saves buying the bundle."""
        return self.individual_total - self.bundle_price
    
    class Meta:
        ordering = ['name']


class BundleItem(models.Model):
    """Items in a product bundle."""
    bundle = models.ForeignKey(ProductBundle, on_delete=models.CASCADE, related_name='bundleitems')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.bundle.name}"
    
    class Meta:
        unique_together = ['bundle', 'product']
