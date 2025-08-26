"""
Django Model Meta Options Practice
Following https://docs.djangoproject.com/en/5.2/ref/models/options/

This module demonstrates all important Meta options available in Django models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


# ==================================================================
# 1. Abstract Base Class Example
# ==================================================================

class TimestampedModel(models.Model):
    """
    Abstract base class that provides self-updating
    'created' and 'modified' fields.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True  # This makes it an abstract base class
        get_latest_by = 'created'  # Default field for latest() and earliest()


# ==================================================================
# 2. Custom Table Names and Database Options
# ==================================================================

class BlogPost(TimestampedModel):
    """
    Blog post model demonstrating custom table name and database options.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    class Meta:
        # Custom table name
        db_table = 'custom_blog_posts'
        
        # Table comment for documentation
        db_table_comment = "Blog posts with custom table name and comprehensive meta options"
        
        # Verbose names for admin and forms
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        
        # Default ordering
        ordering = ['-created', 'title']
        
        # Custom permissions
        permissions = [
            ("can_publish_post", "Can publish blog posts"),
            ("can_feature_post", "Can feature blog posts"),
            ("can_moderate_post", "Can moderate blog posts"),
        ]
        
        # Indexes for performance
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['author', '-created']),
            models.Index(fields=['published', '-views_count']),
            models.Index(fields=['-created'], name='blogpost_created_idx'),
        ]
        
        # Constraints
        constraints = [
            models.CheckConstraint(
                condition=models.Q(views_count__gte=0),
                name='meta_positive_views_count'
            ),
            models.UniqueConstraint(
                fields=['author', 'slug'],
                name='meta_unique_author_slug'
            ),
        ]


# ==================================================================
# 3. Ordering and Related Names
# ==================================================================

class Category(models.Model):
    """
    Category model demonstrating ordering and related names.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
        
        # Custom related name template
        default_related_name = 'categories_%(class)s'
        
        # Unique constraint
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'parent'],
                name='meta_unique_category_name_per_parent'
            )
        ]


class Tag(models.Model):
    """
    Tag model with custom ordering and permissions.
    """
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#000000')  # Hex color
    usage_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-usage_count', 'name']
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        
        # Custom default permissions (no delete permission)
        default_permissions = ('add', 'change', 'view')
        
        indexes = [
            models.Index(fields=['-usage_count']),
            models.Index(fields=['name']),
        ]


# ==================================================================
# 4. Order with Respect To
# ==================================================================

class Question(models.Model):
    """
    Question model for demonstrating order_with_respect_to.
    """
    text = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.text[:50]
    
    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        get_latest_by = 'created'


class Answer(models.Model):
    """
    Answer model demonstrating order_with_respect_to functionality.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    votes = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Answer to: {self.question.text[:30]}"
    
    class Meta:
        # Makes answers orderable with respect to their question
        order_with_respect_to = 'question'
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        
        constraints = [
            models.CheckConstraint(
                condition=models.Q(votes__gte=-100) & models.Q(votes__lte=100),
                name='meta_answer_votes_range'
            )
        ]


# ==================================================================
# 5. Proxy Model Example
# ==================================================================

class PublishedBlogPost(BlogPost):
    """
    Proxy model for published blog posts with custom manager.
    """
    
    class Meta:
        proxy = True
        verbose_name = "Published Blog Post"
        verbose_name_plural = "Published Blog Posts"
        # Proxy models can have different ordering
        ordering = ['-views_count', '-created']
        
        # Custom permissions for proxy model
        permissions = [
            ("can_view_analytics", "Can view blog post analytics"),
        ]
    
    def get_analytics_data(self):
        """Custom method for proxy model."""
        return {
            'views': self.views_count,
            'author': self.author.username,
            'days_since_published': (timezone.now() - self.created).days
        }


# ==================================================================
# 6. Managed and Unmanaged Models
# ==================================================================

class DatabaseView(models.Model):
    """
    Example of an unmanaged model representing a database view.
    """
    post_title = models.CharField(max_length=200)
    author_name = models.CharField(max_length=150)
    category_name = models.CharField(max_length=100)
    view_count = models.PositiveIntegerField()
    
    class Meta:
        managed = False  # Django won't manage this table
        db_table = 'blog_post_summary_view'
        verbose_name = "Blog Post Summary"
        verbose_name_plural = "Blog Post Summaries"
        ordering = ['-view_count']


# ==================================================================
# 7. Advanced Meta Options
# ==================================================================

class Product(models.Model):
    """
    Product model demonstrating advanced meta options.
    """
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    is_active = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        
        # Multiple field ordering
        ordering = ['category__name', 'name']
        
        # Get latest by multiple fields
        get_latest_by = ['-created', '-updated']
        
        # Complex indexes
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price', '-created']),
            models.Index(fields=['sku'], name='product_sku_idx'),
            # Partial index (only for active products)
            models.Index(
                fields=['name'],
                condition=models.Q(is_active=True),
                name='active_product_name_idx'
            ),
        ]
        
        # Multiple constraints
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name='meta_positive_price'
            ),
            models.CheckConstraint(
                condition=models.Q(stock_quantity__gte=0),
                name='meta_positive_stock'
            ),
            models.UniqueConstraint(
                fields=['name', 'category'],
                name='meta_unique_product_name_per_category'
            ),
        ]
        
        # Custom permissions
        permissions = [
            ("can_manage_inventory", "Can manage product inventory"),
            ("can_set_prices", "Can set product prices"),
            ("can_activate_products", "Can activate/deactivate products"),
        ]


# ==================================================================
# 8. Required DB Features and Vendor
# ==================================================================

class PostgreSQLSpecificModel(models.Model):
    """
    Model that only works with PostgreSQL features.
    """
    name = models.CharField(max_length=100)
    json_data = models.JSONField(default=dict)
    
    class Meta:
        # Only create this model on PostgreSQL
        required_db_vendor = 'postgresql'
        verbose_name = "PostgreSQL Specific Model"
        verbose_name_plural = "PostgreSQL Specific Models"


class GISEnabledModel(models.Model):
    """
    Model that requires GIS features.
    """
    name = models.CharField(max_length=100)
    # location = models.PointField()  # Would require GeoDjango
    
    class Meta:
        # Only create this model if GIS is enabled
        required_db_features = ['gis_enabled']
        verbose_name = "GIS Enabled Model"
        verbose_name_plural = "GIS Enabled Models"


# ==================================================================
# 9. Select on Save and Manager Names
# ==================================================================

class CustomManager(models.Manager):
    """Custom manager for demonstration."""
    
    def active(self):
        return self.filter(is_active=True)
    
    def by_priority(self):
        return self.order_by('-priority', 'name')


class ConfigurableModel(models.Model):
    """
    Model demonstrating custom managers and select_on_save.
    """
    name = models.CharField(max_length=100)
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Custom managers
    objects = models.Manager()  # Default manager
    custom = CustomManager()   # Custom manager
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Configurable Model"
        verbose_name_plural = "Configurable Models"
        
        # Specify which manager to use as default
        default_manager_name = 'objects'
        base_manager_name = 'custom'
        
        # Use old save algorithm (rarely needed)
        select_on_save = False
        
        ordering = ['-priority', 'name']
        
        indexes = [
            models.Index(fields=['priority', 'is_active']),
        ]


# ==================================================================
# 10. Complete Example with All Meta Options
# ==================================================================

class CompleteExampleModel(TimestampedModel):
    """
    Comprehensive example showing most Meta options in one model.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    priority = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    class Meta:
        # Table configuration
        db_table = 'complete_example'
        db_table_comment = "Complete example demonstrating all Meta options"
        
        # Naming
        verbose_name = "Complete Example"
        verbose_name_plural = "Complete Examples"
        
        # Ordering
        ordering = ['-is_featured', '-priority', '-created']
        get_latest_by = ['-created', '-modified']
        
        # Permissions
        permissions = [
            ("can_feature", "Can feature items"),
            ("can_set_priority", "Can set priority"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view')
        
        # Database optimization
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['-priority', '-created']),
            models.Index(fields=['is_featured', '-view_count']),
            models.Index(
                fields=['title'],
                condition=models.Q(is_active=True),
                name='active_complete_title_idx'
            ),
        ]
        
        # Constraints
        constraints = [
            models.CheckConstraint(
                condition=models.Q(priority__gte=0) & models.Q(priority__lte=10),
                name='meta_priority_range_0_to_10'
            ),
            models.CheckConstraint(
                condition=models.Q(view_count__gte=0),
                name='meta_positive_view_count'
            ),
            models.UniqueConstraint(
                fields=['title', 'category'],
                condition=models.Q(is_active=True),
                name='meta_unique_active_title_per_category'
            ),
        ]


# ==================================================================
# 11. Legacy Examples (for completeness)
# ==================================================================

class LegacyModel(models.Model):
    """
    Example showing legacy Meta options (still supported but not recommended).
    """
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    class Meta:
        verbose_name = "Legacy Model"
        verbose_name_plural = "Legacy Models"
        
        # Legacy constraint (use constraints instead)
        unique_together = [
            ['name', 'email'],  # Better to use UniqueConstraint
        ]
        
        # This is fine but constraints provide more options
        # unique_together = ['name', 'email']  # Single constraint syntax
