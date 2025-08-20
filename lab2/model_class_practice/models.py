"""
Django Model Class Methods and Attributes Practice
Following https://docs.djangoproject.com/en/5.2/ref/models/class/ and instances/

This module demonstrates all important Model class methods and attributes.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
import uuid


# ==================================================================
# 1. Basic Model with Core Methods
# ==================================================================

class Article(models.Model):
    """
    Article model demonstrating core Model methods and attributes.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    published_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    
    # Choices for status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    class Meta:
        ordering = ['-created']
        get_latest_by = 'created'
        verbose_name = "Article"
        verbose_name_plural = "Articles"
    
    def __str__(self):
        """String representation of the model."""
        return self.title
    
    def __repr__(self):
        """Developer-friendly representation."""
        return f"<Article: {self.title} (id={self.pk})>"
    
    def save(self, *args, **kwargs):
        """
        Override save method to demonstrate custom save behavior.
        """
        # Auto-publish logic
        if self.status == 'published' and not self.published_date:
            self.published_date = timezone.now()
        elif self.status != 'published':
            self.published_date = None
            
        super().save(*args, **kwargs)
    
    def delete(self, using=None, keep_parents=False):
        """
        Override delete method for custom deletion behavior.
        """
        # Log deletion (in real app, you'd use proper logging)
        print(f"Deleting article: {self.title}")
        return super().delete(using=using, keep_parents=keep_parents)
    
    def clean(self):
        """
        Model validation logic.
        """
        # Custom validation
        if self.status == 'published' and not self.content.strip():
            raise ValidationError({
                'content': _('Published articles must have content.')
            })
        
        # Cross-field validation
        if self.published_date and self.published_date > timezone.now():
            raise ValidationError({
                'published_date': _('Published date cannot be in the future.')
            })
    
    def get_absolute_url(self):
        """
        Return the canonical URL for this article.
        """
        try:
            return reverse('article-detail', kwargs={'slug': self.slug})
        except:
            # Fallback for when URLs are not configured
            return f"/articles/{self.slug}/"
    
    def get_status_display_custom(self):
        """
        Custom method to demonstrate get_FOO_display() pattern.
        """
        status_icons = {
            'draft': '📝',
            'review': '👀',
            'published': '✅',
            'archived': '📦',
        }
        display = self.get_status_display()
        icon = status_icons.get(self.status, '❓')
        return f"{icon} {display}"
    
    def increment_view_count(self):
        """
        Demonstrate updating attributes based on existing fields.
        """
        from django.db.models import F
        # Using F expression to avoid race conditions
        Article.objects.filter(pk=self.pk).update(view_count=F('view_count') + 1)
        # Refresh the instance to get updated value
        self.refresh_from_db(fields=['view_count'])
    
    @classmethod
    def create_draft(cls, title, content, author):
        """
        Class method for creating draft articles.
        """
        slug = title.lower().replace(' ', '-')
        return cls.objects.create(
            title=title,
            slug=slug,
            content=content,
            author=author,
            status='draft'
        )


# ==================================================================
# 2. Model with Custom Managers and Exceptions
# ==================================================================

class PublishedArticleManager(models.Manager):
    """Custom manager for published articles."""
    
    def get_queryset(self):
        return super().get_queryset().filter(status='published')
    
    def by_author(self, author):
        return self.get_queryset().filter(author=author)


class Book(models.Model):
    """
    Book model demonstrating DoesNotExist and MultipleObjectsReturned exceptions.
    """
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    author = models.CharField(max_length=100)
    publication_date = models.DateField()
    pages = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    
    # Managers
    objects = models.Manager()  # Default manager
    published_books = PublishedArticleManager()  # Custom manager
    
    class Meta:
        ordering = ['title']
        get_latest_by = 'publication_date'
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def __eq__(self, other):
        """
        Demonstrate custom equality comparison.
        """
        if not isinstance(other, Book):
            return False
        return self.isbn == other.isbn
    
    def __hash__(self):
        """
        Demonstrate custom hashing based on ISBN.
        """
        if self.isbn:
            return hash(self.isbn)
        return super().__hash__()
    
    @classmethod
    def find_by_isbn(cls, isbn):
        """
        Demonstrate DoesNotExist exception handling.
        """
        try:
            return cls.objects.get(isbn=isbn)
        except cls.DoesNotExist:
            return None
        except cls.MultipleObjectsReturned:
            # This shouldn't happen with unique ISBN, but for demonstration
            return cls.objects.filter(isbn=isbn).first()


# ==================================================================
# 3. Model with Date-based Navigation
# ==================================================================

class Event(models.Model):
    """
    Event model demonstrating get_next_by_FOO and get_previous_by_FOO methods.
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    max_attendees = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['event_date']
        get_latest_by = 'event_date'
    
    def __str__(self):
        return f"{self.name} on {self.event_date.strftime('%Y-%m-%d')}"
    
    def get_next_event(self):
        """
        Get the next event after this one.
        """
        try:
            return self.get_next_by_event_date()
        except Event.DoesNotExist:
            return None
    
    def get_previous_event(self):
        """
        Get the previous event before this one.
        """
        try:
            return self.get_previous_by_event_date()
        except Event.DoesNotExist:
            return None


# ==================================================================
# 4. Model with Advanced Validation
# ==================================================================

class Product(models.Model):
    """
    Product model demonstrating comprehensive validation methods.
    """
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name='model_class_positive_price'
            ),
            models.CheckConstraint(
                condition=models.Q(cost__gte=0),
                name='model_class_positive_cost'
            ),
        ]
    
    def __str__(self):
        return f"{self.name} (SKU: {self.sku})"
    
    def clean_fields(self, exclude=None):
        """
        Demonstrate clean_fields override.
        """
        super().clean_fields(exclude=exclude)
        
        # Custom field validation
        if exclude is None:
            exclude = []
            
        if 'price' not in exclude and self.price and self.price < 0:
            raise ValidationError({
                'price': _('Price must be positive.')
            })
    
    def clean(self):
        """
        Model-level validation.
        """
        super().clean()
        
        # Business logic validation
        if self.price and self.cost and self.price < self.cost:
            raise ValidationError(
                _('Selling price cannot be lower than cost price.')
            )
        
        if self.stock_quantity < 0:
            raise ValidationError({
                'stock_quantity': _('Stock quantity cannot be negative.')
            })
    
    def validate_unique(self, exclude=None):
        """
        Demonstrate validate_unique override.
        """
        super().validate_unique(exclude=exclude)
        
        # Custom uniqueness validation
        if not exclude or 'sku' not in exclude:
            # Additional SKU format validation
            if self.sku and not self.sku.isupper():
                raise ValidationError({
                    'sku': _('SKU must be in uppercase.')
                })
    
    def full_clean(self, exclude=None, validate_unique=True, validate_constraints=True):
        """
        Demonstrate full_clean override.
        """
        # Add custom pre-validation logic here
        if self.sku:
            self.sku = self.sku.upper()
        
        super().full_clean(exclude, validate_unique, validate_constraints)
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage."""
        if self.cost and self.cost > 0:
            return ((self.price - self.cost) / self.cost) * 100
        return 0
    
    def is_low_stock(self):
        """Check if product is low on stock."""
        return self.stock_quantity <= self.min_stock_level


# ==================================================================
# 5. Model with Custom Primary Key
# ==================================================================

class Profile(models.Model):
    """
    Profile model demonstrating custom primary key handling.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['user__username']
    
    def __str__(self):
        return f"Profile for {self.user.username}"
    
    def get_absolute_url(self):
        try:
            return reverse('profile-detail', kwargs={'uuid': self.uuid})
        except:
            # Fallback for when URLs are not configured
            return f"/profiles/{self.uuid}/"
    
    def save(self, *args, **kwargs):
        """
        Demonstrate pk property usage with custom primary key.
        """
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new:
            print(f"Created new profile with UUID: {self.pk}")


# ==================================================================
# 6. Model with State Tracking
# ==================================================================

class Order(models.Model):
    """
    Order model demonstrating _state attribute usage.
    """
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        """
        Demonstrate _state attribute usage.
        """
        # Check if this is a new instance
        if self._state.adding:
            print(f"Creating new order: {self.order_number}")
            # Generate order number if not provided
            if not self.order_number:
                self.order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        else:
            print(f"Updating existing order: {self.order_number}")
        
        # Check which database the instance came from
        if self._state.db:
            print(f"Instance loaded from database: {self._state.db}")
        
        super().save(*args, **kwargs)
    
    def is_editable(self):
        """Check if order can still be edited."""
        return self.status in ['pending', 'processing']
    
    @classmethod
    def from_db(cls, db, field_names, values):
        """
        Demonstrate from_db customization.
        """
        instance = super().from_db(db, field_names, values)
        
        # Store original values for change tracking
        instance._original_values = dict(zip(field_names, values))
        
        return instance
    
    def get_changed_fields(self):
        """Get fields that have changed since loading from database."""
        if not hasattr(self, '_original_values'):
            return []
        
        changed = []
        for field in self._meta.fields:
            if field.name in self._original_values:
                original = self._original_values[field.name]
                current = getattr(self, field.name)
                if original != current:
                    changed.append(field.name)
        
        return changed


# ==================================================================
# 7. Model with Refresh and Deferred Fields
# ==================================================================

class Analytics(models.Model):
    """
    Analytics model demonstrating refresh_from_db and deferred fields.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date = models.DateField()
    page_views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    bounce_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_time_on_page = models.DurationField(default=timezone.timedelta)
    computed_score = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ['article', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.article.title} on {self.date}"
    
    def refresh_from_db(self, using=None, fields=None, **kwargs):
        """
        Override refresh_from_db to demonstrate custom behavior.
        """
        # If any specific field is being refreshed, refresh all analytics fields
        if fields is not None:
            analytics_fields = {'page_views', 'unique_visitors', 'bounce_rate', 'avg_time_on_page'}
            if any(field in analytics_fields for field in fields):
                fields = list(set(fields) | analytics_fields)
        
        super().refresh_from_db(using, fields, **kwargs)
        
        # Recalculate computed score after refresh
        self.update_computed_score()
    
    def update_computed_score(self):
        """Calculate a composite analytics score."""
        if self.unique_visitors > 0:
            bounce_decimal = float(self.bounce_rate) / 100
            engagement = (1 - bounce_decimal) * (self.page_views / self.unique_visitors)
            self.computed_score = float(engagement * 100)
        else:
            self.computed_score = 0.0
    
    def save(self, *args, **kwargs):
        """Auto-calculate computed score on save."""
        self.update_computed_score()
        super().save(*args, **kwargs)


# ==================================================================
# 8. Model for Testing Pickling
# ==================================================================

class SimpleNote(models.Model):
    """
    Simple model for demonstrating pickling behavior.
    """
    title = models.CharField(max_length=100)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    priority = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['-priority', '-created']
    
    def __str__(self):
        return self.title
    
    def get_priority_display(self):
        """Custom display method."""
        priority_names = {
            1: 'Low',
            2: 'Medium', 
            3: 'High',
            4: 'Critical'
        }
        return priority_names.get(self.priority, 'Unknown')


# ==================================================================
# 9. Abstract Model for Inheritance Testing
# ==================================================================

class TimestampedModel(models.Model):
    """
    Abstract model demonstrating inheritance patterns.
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        get_latest_by = 'created'
    
    def age_in_days(self):
        """Calculate age in days."""
        return (timezone.now() - self.created).days


class BlogPost(TimestampedModel):
    """
    BlogPost inheriting from TimestampedModel.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='model_class_blog_posts')
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        try:
            return reverse('blogpost-detail', kwargs={'pk': self.pk})
        except:
            # Fallback for when URLs are not configured
            return f"/blog/{self.pk}/"
