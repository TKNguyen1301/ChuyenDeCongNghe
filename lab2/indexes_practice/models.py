from django.db import models
from django.db.models import Index, Q, F
from django.db.models.functions import Lower, Upper, Length, Coalesce
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

# =============================================================================
# DJANGO INDEXES PRACTICE - Tối ưu hóa Database Performance
# =============================================================================

class Article(models.Model):
    """
    Model Article với các loại indexes khác nhau
    Demonstrating various index types for database optimization
    """
    
    # Basic fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    summary = models.TextField(blank=True)
    
    # Status và category cho partial indexes
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    category = models.CharField(max_length=50)
    
    # Datetime fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Numeric fields cho functional indexes
    view_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    word_count = models.PositiveIntegerField(default=0)
    
    # Boolean field
    is_featured = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    
    # Text field for full-text search
    tags = models.CharField(max_length=200, blank=True)
    
    class Meta:
        # Các loại indexes khác nhau
        indexes = [
            # 1. Simple field index (B-Tree default)
            Index(fields=['status']),
            Index(fields=['category']),
            Index(fields=['created_at']),
            
            # 2. Composite/Multi-column indexes
            Index(fields=['status', 'category']),
            Index(fields=['category', '-created_at']),  # Descending order
            Index(fields=['status', '-published_at', 'is_featured']),
            
            # 3. Partial indexes (với condition)
            Index(
                fields=['title', 'slug'],
                condition=Q(status='published'),
                name='published_articles_idx'
            ),
            Index(
                fields=['rating'],
                condition=Q(rating__gte=4.0),
                name='high_rating_articles_idx'
            ),
            Index(
                fields=['view_count'],
                condition=Q(view_count__gt=1000) & Q(is_featured=True),
                name='popular_featured_articles_idx'
            ),
            
            # 4. Functional indexes (với expressions)
            Index(
                Lower('title').desc(),
                name='lower_title_idx'
            ),
            Index(
                Length('content'),
                name='content_length_idx'
            ),
            Index(
                F('view_count') * F('rating'),
                name='popularity_score_idx'
            ),
            
            # 5. Covering indexes (với include - PostgreSQL only)
            Index(
                fields=['status'],
                include=['title', 'created_at'],
                name='status_covering_idx'
            ),
            Index(
                fields=['category', 'status'],
                include=['title', 'summary', 'view_count'],
                name='category_status_covering_idx'
            ),
            
            # 6. Complex functional index
            Index(
                Upper('category'),
                Coalesce('published_at', 'created_at'),
                name='category_publish_date_idx'
            ),
        ]
        
        # Ordering default
        ordering = ['-created_at', 'title']
        
        # Constraints
        constraints = [
            models.CheckConstraint(
                check=Q(rating__gte=0) & Q(rating__lte=5),
                name='rating_range'
            ),
            models.CheckConstraint(
                check=Q(view_count__gte=0),
                name='view_count_positive'
            ),
        ]
    
    def __str__(self):
        return self.title

class Product(models.Model):
    """
    Product model với indexes tối ưu cho e-commerce
    """
    
    # Product info
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=20, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_digital = models.BooleanField(default=False)
    
    # Categories and tags
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    launch_date = models.DateField(null=True, blank=True)
    
    # Analytics
    sales_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        indexes = [
            # Basic indexes cho filtering thường xuyên
            Index(fields=['is_active']),
            Index(fields=['category']),
            Index(fields=['brand']),
            
            # E-commerce specific indexes
            Index(fields=['price']),
            Index(fields=['stock_quantity']),
            Index(fields=['sales_count']),
            
            # Composite indexes cho queries phức tạp
            Index(fields=['category', 'subcategory']),
            Index(fields=['is_active', 'category', '-price']),
            Index(fields=['brand', 'category', '-created_at']),
            
            # Partial indexes cho business logic
            Index(
                fields=['price', 'stock_quantity'],
                condition=Q(is_active=True) & Q(stock_quantity__gt=0),
                name='available_products_idx'
            ),
            Index(
                fields=['discount_percentage'],
                condition=Q(discount_percentage__gt=0) & Q(is_active=True),
                name='discounted_products_idx'
            ),
            Index(
                fields=['sales_count'],
                condition=Q(sales_count__gte=100),
                name='bestseller_products_idx'
            ),
            
            # Functional indexes cho calculations
            Index(
                F('price') * (100 - F('discount_percentage')) / 100,
                name='final_price_idx'
            ),
            Index(
                F('price') - F('cost'),
                name='profit_margin_idx'
            ),
            
            # Covering indexes cho performance
            Index(
                fields=['category'],
                include=['name', 'price', 'stock_quantity'],
                name='category_details_cover_idx'
            ),
        ]
        
        ordering = ['-sales_count', 'name']

class Customer(models.Model):
    """
    Customer model với indexes cho CRM và analytics
    """
    
    # Personal info
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Location
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Customer status
    is_active = models.BooleanField(default=True)
    is_vip = models.BooleanField(default=False)
    customer_tier = models.CharField(
        max_length=20,
        choices=[
            ('bronze', 'Bronze'),
            ('silver', 'Silver'),
            ('gold', 'Gold'),
            ('platinum', 'Platinum'),
        ],
        default='bronze'
    )
    
    # Dates
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    last_purchase = models.DateTimeField(null=True, blank=True)
    
    # Analytics
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lifetime_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        indexes = [
            # Customer management indexes
            Index(fields=['is_active']),
            Index(fields=['customer_tier']),
            Index(fields=['is_vip']),
            
            # Location-based indexes
            Index(fields=['country', 'city']),
            Index(fields=['postal_code']),
            
            # Time-based indexes
            Index(fields=['-date_joined']),
            Index(fields=['-last_purchase']),
            
            # Analytics indexes
            Index(fields=['-total_spent']),
            Index(fields=['-lifetime_value']),
            Index(fields=['-total_orders']),
            
            # Business intelligence indexes
            Index(fields=['customer_tier', '-total_spent']),
            Index(fields=['country', 'customer_tier']),
            
            # Partial indexes cho segmentation
            Index(
                fields=['total_spent', 'total_orders'],
                condition=Q(is_active=True),
                name='active_customers_analytics'
            ),
            Index(
                fields=['last_purchase'],
                condition=Q(total_orders__gte=5),
                name='repeat_customers_idx'
            ),
            Index(
                fields=['lifetime_value'],
                condition=Q(lifetime_value__gte=1000000),  # 1M VND
                name='high_value_customers_idx'
            ),
            
            # Functional indexes
            Index(
                F('total_spent') / F('total_orders'),
                condition=Q(total_orders__gt=0),
                name='average_order_value_idx'
            ),
            
            # Covering indexes cho reports
            Index(
                fields=['country'],
                include=['customer_tier', 'total_spent', 'total_orders'],
                name='country_analytics_cover_idx'
            ),
            Index(
                fields=['customer_tier'],
                include=['first_name', 'last_name', 'email', 'total_spent'],
                name='tier_customer_cover_idx'
            ),
        ]
        
        ordering = ['-lifetime_value', 'last_name', 'first_name']

class Order(models.Model):
    """
    Order model với indexes cho order management và reporting
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    
    # Order details
    order_number = models.CharField(max_length=50, unique=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Financial
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Shipping
    shipping_method = models.CharField(max_length=50, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Analytics
    items_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        indexes = [
            # Order management indexes
            Index(fields=['status']),
            Index(fields=['customer', 'status']),
            Index(fields=['-created_at']),
            Index(fields=['order_number']),
            
            # Financial reporting indexes
            Index(fields=['-total_amount']),
            Index(fields=['created_at', 'total_amount']),
            Index(fields=['status', '-total_amount']),
            
            # Shipping indexes
            Index(fields=['shipping_method']),
            Index(fields=['tracking_number']),
            Index(fields=['shipped_at']),
            Index(fields=['delivered_at']),
            
            # Time-based analysis indexes
            Index(fields=['created_at', 'status']),
            Index(fields=['-created_at', 'customer']),
            
            # Business reporting indexes
            Index(fields=['customer', '-created_at']),
            Index(fields=['status', 'shipping_method']),
            
            # Partial indexes cho active orders
            Index(
                fields=['created_at', 'total_amount'],
                condition=Q(status__in=['pending', 'processing', 'shipped']),
                name='active_orders_idx'
            ),
            Index(
                fields=['customer', 'total_amount'],
                condition=Q(status='delivered'),
                name='completed_orders_cust_idx'
            ),
            Index(
                fields=['tracking_number'],
                condition=Q(status__in=['shipped', 'delivered']) & ~Q(tracking_number=''),
                name='tracked_orders_idx'
            ),
            
            # Functional indexes cho analytics
            Index(
                F('total_amount') / F('items_count'),
                condition=Q(items_count__gt=0),
                name='average_item_price_idx'
            ),
            Index(
                F('tax_amount') + F('shipping_cost'),
                name='additional_costs_idx'
            ),
            
            # Covering indexes cho reports
            Index(
                fields=['status'],
                include=['total_amount', 'created_at', 'items_count'],
                name='status_summary_cover_idx'
            ),
            Index(
                fields=['customer'],
                include=['order_number', 'total_amount', 'status', 'created_at'],
                name='customer_orders_cover_idx'
            ),
        ]
        
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer.email}"

class LogEntry(models.Model):
    """
    Log model với indexes cho monitoring và debugging
    """
    
    # Log details
    LEVEL_CHOICES = [
        ('debug', 'DEBUG'),
        ('info', 'INFO'),
        ('warning', 'WARNING'),
        ('error', 'ERROR'),
        ('critical', 'CRITICAL'),
    ]
    
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    message = models.TextField()
    module = models.CharField(max_length=100)
    function = models.CharField(max_length=100, blank=True)
    
    # Context
    user_id = models.PositiveIntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)  # Request duration
    
    # Additional data
    extra_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        indexes = [
            # Monitoring indexes
            Index(fields=['level']),
            Index(fields=['-timestamp']),
            Index(fields=['module']),
            Index(fields=['user_id']),
            
            # Performance monitoring
            Index(fields=['duration_ms']),
            Index(fields=['request_path']),
            
            # Time-based queries
            Index(fields=['timestamp', 'level']),
            Index(fields=['-timestamp', 'module']),
            
            # Debugging indexes
            Index(fields=['module', 'function']),
            Index(fields=['ip_address', '-timestamp']),
            
            # Partial indexes cho errors
            Index(
                fields=['-timestamp'],
                condition=Q(level__in=['error', 'critical']),
                name='error_logs_idx'
            ),
            Index(
                fields=['module', 'function'],
                condition=Q(level='error'),
                name='error_source_idx'
            ),
            Index(
                fields=['user_id', '-timestamp'],
                condition=Q(level__in=['warning', 'error', 'critical']),
                name='user_issues_idx'
            ),
            
            # Performance analysis
            Index(
                fields=['duration_ms'],
                condition=Q(duration_ms__gte=1000),  # Slow requests > 1s
                name='slow_requests_idx'
            ),
            
            # Functional indexes
            Index(
                Length('message'),
                name='message_length_idx'
            ),
            
            # Covering indexes cho dashboard
            Index(
                fields=['level'],
                include=['timestamp', 'module', 'message'],
                name='log_dashboard_cover_idx'
            ),
        ]
        
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.level.upper()} - {self.module} - {self.timestamp}"
