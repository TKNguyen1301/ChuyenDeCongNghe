from django.db import models
from datetime import date, datetime
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Index, Q, F
from django.db.models.functions import Lower, Upper, Concat, Round, Length

# Create your models here.

# Ví dụ đầu tiên từ Django documentation với custom methods
class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateField(default=date(1990, 1, 1))
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    # Custom method từ Django docs
    def baby_boomer_status(self):
        "Returns the person's baby-boomer status."
        if self.birth_date < date(1945, 8, 1):
            return "Pre-boomer"
        elif self.birth_date < date(1965, 1, 1):
            return "Baby boomer"
        else:
            return "Post-boomer"
    
    @property
    def full_name(self):
        "Returns the person's full name."
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        "Returns the person's age."
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))


# Model với nhiều field types khác nhau và Meta options
class Student(models.Model):
    YEAR_IN_SCHOOL_CHOICES = [
        ("FR", "Freshman"),
        ("SO", "Sophomore"), 
        ("JR", "Junior"),
        ("SR", "Senior"),
        ("GR", "Graduate"),
    ]
    
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    email = models.EmailField(unique=True)
    birth_date = models.DateField()
    year_in_school = models.CharField(
        max_length=2,
        choices=YEAR_IN_SCHOOL_CHOICES,
        default="FR",
    )
    is_active = models.BooleanField(default=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Student"
        verbose_name_plural = "Students"
        db_table = 'student_table'
    
    def __str__(self):
        return self.name
    
    def get_year_display_custom(self):
        return f"Year: {self.get_year_in_school_display()}"


# Abstract base class example từ Django docs
class CommonInfo(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()

    class Meta:
        abstract = True
        ordering = ['name']


class StudentInherited(CommonInfo):
    home_group = models.CharField(max_length=5)
    
    class Meta(CommonInfo.Meta):
        db_table = 'student_inherited'


# One-to-One relationship example từ Django docs
class Place(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.name} the place"


class Restaurant(Place):
    serves_hot_dogs = models.BooleanField(default=False)
    serves_pizza = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} the restaurant"


class Waiter(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} at {self.restaurant}"


# Model với custom save method
class Blog(models.Model):
    name = models.CharField(max_length=100)
    tagline = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Custom logic trước khi save
        if self.name == "Forbidden Blog":
            return  # Không cho phép tạo blog này
        else:
            super().save(*args, **kwargs)  # Gọi save() method gốc
    
    def __str__(self):
        return self.name


# Model để demo relationships với verbose names
class Manufacturer(models.Model):
    name = models.CharField("manufacturer name", max_length=100)
    country = models.CharField(max_length=50)
    founded_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Car Manufacturer"
        verbose_name_plural = "Car Manufacturers"
    
    def __str__(self):
        return self.name


class Car(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.ForeignKey(
        Manufacturer, 
        on_delete=models.CASCADE,
        verbose_name="the related manufacturer"
    )
    year = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_electric = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['manufacturer', 'name']
        unique_together = ['manufacturer', 'name', 'year']
    
    def __str__(self):
        return f"{self.manufacturer.name} {self.name}"
    
    @property
    def is_vintage(self):
        return self.year < 1990


# Many-to-Many relationships example từ Django docs
class Topping(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name


class Pizza(models.Model):
    name = models.CharField(max_length=100)
    toppings = models.ManyToManyField(Topping)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return self.name


# Many-to-Many with intermediate model (từ Django docs)
class Group(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(Person, through="Membership")

    def __str__(self):
        return self.name


class Membership(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateField()
    invite_reason = models.CharField(max_length=64)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["person", "group"], name="unique_person_group"
            )
        ]


# ============ CÁC FIELD TYPES ADVANCED TỪNG ĐƯỢC ĐỀ CẬP TRONG TÀI LIỆU ============

# Model với UUID field và các field numeric khác
class Product(models.Model):
    # UUIDField cho primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # CharField với các options khác nhau
    name = models.CharField(max_length=200, db_index=True, help_text="Tên sản phẩm")
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    
    # Text field cho mô tả dài
    description = models.TextField(blank=True, null=True)
    
    # Các field số với ràng buộc
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    weight = models.FloatField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    
    # BigInteger field cho các số lớn
    total_sold = models.BigIntegerField(default=0)
    rating_count = models.PositiveBigIntegerField(default=0)
    
    # SmallInteger field
    category_priority = models.SmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Boolean field
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # URL field
    external_url = models.URLField(blank=True, null=True)
    
    # Email field cho contact
    contact_email = models.EmailField(blank=True, null=True)
    
    # Date và DateTime fields với auto options
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    release_date = models.DateField(null=True, blank=True)
    
    # Time field
    daily_update_time = models.TimeField(null=True, blank=True)
    
    # Duration field
    warranty_period = models.DurationField(null=True, blank=True, help_text="Thời gian bảo hành")
    
    # JSONField cho metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Binary field (ít dùng nhưng có trong docs)
    custom_data = models.BinaryField(null=True, blank=True, editable=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
        
        # Basic field indexes
        indexes = [
            # Simple field index
            Index(fields=['name'], name='product_name_idx'),
            # Descending order index
            Index(fields=['-created_at'], name='product_created_desc_idx'),
            # Composite index
            Index(fields=['is_active', 'is_featured'], name='product_status_idx'),
            # Partial index với condition
            Index(fields=['price'], condition=Q(is_active=True), name='active_product_price_idx'),
            # Functional index với expressions
            Index(Lower('name'), name='product_lower_name_idx'),
            # Multiple field with mixed ordering
            Index(fields=['category_priority', '-price'], name='product_priority_price_idx'),
        ]
        
    def __str__(self):
        return self.name


# Model với IP Address field
class ServerLog(models.Model):
    # GenericIPAddressField 
    client_ip = models.GenericIPAddressField(protocol='both')  # Hỗ trợ IPv4 và IPv6
    server_ip = models.GenericIPAddressField(protocol='IPv4')  # Chỉ IPv4
    
    # Auto field (thường Django tự tạo, nhưng có thể định nghĩa rõ)
    log_id = models.AutoField(primary_key=True)
    
    # CharField (bỏ db_collation vì SQLite không hỗ trợ)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    
    # TextField với db_comment
    message = models.TextField(db_comment="Log message content")
    
    # IntegerField với db_default (Django 4.2+)
    status_code = models.IntegerField(default=200)
    
    # DateTime với unique_for_date
    timestamp = models.DateTimeField(default=now)
    log_date = models.DateField(auto_now_add=True)
    
    # CharField với unique_for_date
    daily_sequence = models.CharField(max_length=10, unique_for_date='log_date')
    
    class Meta:
        verbose_name = "Server Log"
        verbose_name_plural = "Server Logs"
        
        indexes = [
            # IP address search index
            Index(fields=['client_ip'], name='serverlog_client_ip_idx'),
            # Status code index
            Index(fields=['status_code'], name='serverlog_status_idx'),
            # Time-based indexes
            Index(fields=['-timestamp'], name='serverlog_timestamp_desc_idx'),
            Index(fields=['log_date', 'daily_sequence'], name='serverlog_daily_seq_idx'),
            # Composite index for filtering
            Index(fields=['status_code', '-timestamp'], name='serverlog_status_time_idx'),
            # Partial index for errors only
            Index(fields=['timestamp'], condition=Q(status_code__gte=400), name='serverlog_errors_idx'),
        ]


# Model với FileField và ImageField
class Document(models.Model):
    DOCUMENT_TYPES = [
        ('PDF', 'PDF Document'),
        ('DOC', 'Word Document'),
        ('XLS', 'Excel File'),
        ('IMG', 'Image File'),
    ]
    
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=3, choices=DOCUMENT_TYPES, default='PDF')
    
    # FileField với upload_to function
    def user_directory_path(instance, filename):
        return f'documents/{instance.document_type}/{filename}'
    
    file = models.FileField(upload_to=user_directory_path, max_length=500)
    
    # ImageField với height_field và width_field
    thumbnail = models.ImageField(
        upload_to='thumbnails/',
        height_field='thumbnail_height',
        width_field='thumbnail_width',
        null=True,
        blank=True
    )
    thumbnail_height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    thumbnail_width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    
    # FilePathField
    template_path = models.FilePathField(
        path='/templates/',
        match=r".*\.html$",
        recursive=True,
        allow_files=True,
        allow_folders=False,
        null=True,
        blank=True
    )
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


# Model sử dụng Enumeration choices (Django 3.0+)
class Order(models.Model):
    # TextChoices enumeration
    class Status(models.TextChoices):
        PENDING = 'PD', 'Pending'
        PROCESSING = 'PR', 'Processing'
        SHIPPED = 'SH', 'Shipped'
        DELIVERED = 'DL', 'Delivered'
        CANCELLED = 'CN', 'Cancelled'
    
    # IntegerChoices enumeration
    class Priority(models.IntegerChoices):
        LOW = 1, 'Low'
        NORMAL = 2, 'Normal'
        HIGH = 3, 'High'
        URGENT = 4, 'Urgent'
    
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.PENDING)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.NORMAL)
    
    # ForeignKey với các tùy chọn khác nhau
    customer = models.ForeignKey(
        Person, 
        on_delete=models.PROTECT,  # Không cho phép xóa Person nếu có Order
        related_name='orders',
        related_query_name='order'
    )
    
    # ForeignKey với SET_NULL
    assigned_staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders'
    )
    
    products = models.ManyToManyField(Product, through='OrderItem')
    
    # Decimal field với validation
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    order_date = models.DateTimeField(auto_now_add=True)
    
    def is_high_priority(self):
        return self.priority >= self.Priority.HIGH
    
    class Meta:
        ordering = ['-order_date', '-priority']
        
        indexes = [
            # Order number index (unique searches)
            Index(fields=['order_number'], name='order_number_idx'),
            # Status and priority indexes
            Index(fields=['status'], name='order_status_idx'),
            Index(fields=['priority'], name='order_priority_idx'),
            # Customer relationship index
            Index(fields=['customer'], name='order_customer_idx'),
            # Date-based indexes
            Index(fields=['-order_date'], name='order_date_desc_idx'),
            # Composite indexes for common queries
            Index(fields=['status', '-order_date'], name='order_status_date_idx'),
            Index(fields=['customer', '-order_date'], name='order_customer_date_idx'),
            # Partial index for active orders
            Index(fields=['priority'], condition=Q(status__in=['PD', 'PR']), name='active_order_priority_idx'),
            # Amount-based index for reporting
            Index(fields=['-total_amount'], name='order_amount_desc_idx'),
        ]
    
    def __str__(self):
        return f"Order {self.order_number} - {self.get_status_display()}"


# Through model cho ManyToMany relationship
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Calculated field
    @property
    def total_price(self):
        return self.quantity * self.unit_price
    
    class Meta:
        unique_together = [['order', 'product']]
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# Custom validator function
def validate_birth_date(value):
    if value and value > date.today():
        raise ValueError("Ngày sinh không được trong tương lai")

# Model với custom validation và error messages
class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        primary_key=True
    )
    
    # CharField với custom error messages
    phone = models.CharField(
        max_length=15, 
        blank=True,
        error_messages={
            'max_length': 'Số điện thoại không được vượt quá 15 ký tự.',
        }
    )
    
    # DateField với custom validation
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        validators=[validate_birth_date]
    )
    
    # CharField với choices từ function
    def get_country_choices():
        return [
            ('VN', 'Vietnam'),
            ('US', 'United States'),
            ('JP', 'Japan'),
            ('KR', 'South Korea'),
        ]
    
    country = models.CharField(
        max_length=2,
        choices=get_country_choices,
        default='VN'
    )
    
    # JSONField với default function
    def default_preferences():
        return {
            'language': 'vi',
            'timezone': 'Asia/Ho_Chi_Minh',
            'notifications': True
        }
    
    preferences = models.JSONField(default=default_preferences)
    
    # CharField với unique_for_year
    membership_code = models.CharField(
        max_length=10, 
        unique_for_year='date_joined',
        null=True,
        blank=True
    )
    date_joined = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"


# Model inheritance example - Abstract base class
class TimeStampedModel(models.Model):
    """Abstract base class với timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


# Model kế thừa từ abstract class
class Article(TimeStampedModel):
    title = models.CharField(max_length=200, unique_for_date='published_date')
    content = models.TextField()
    published_date = models.DateField()
    
    # SlugField với prepopulated
    slug = models.SlugField(max_length=200, unique=True)
    
    # ManyToMany với limit_choices_to
    authors = models.ManyToManyField(
        Person,
        limit_choices_to={'birth_date__year__gte': 1980},  # Chỉ những người sinh từ 1980
        related_name='articles'
    )
    
    def __str__(self):
        return self.title


# Model với custom manager và Meta options nâng cao
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class BlogPost(TimeStampedModel):
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_published = models.BooleanField(default=False)
    author = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='blog_posts')
    
    # Multiple managers
    objects = models.Manager()  # Default manager
    published = PublishedManager()  # Custom manager
    
    class Meta:
        # Advanced Meta options
        db_table = 'custom_blog_posts'
        indexes = [
            # Basic indexes
            Index(fields=['title', 'is_published'], name='blog_title_published_idx'),
            Index(fields=['-created_at'], name='blog_created_desc_idx'),
            # Functional indexes
            Index(Lower('title'), name='blog_lower_title_idx'),
            # Partial indexes
            Index(fields=['author'], condition=Q(is_published=True), name='blog_published_author_idx'),
            Index(fields=['-created_at'], condition=Q(is_published=True), name='blog_published_recent_idx'),
            # Text search preparation
            Index(fields=['title'], name='blog_title_search_idx'),
        ]
        # Bỏ CheckConstraint vì SQLite không hỗ trợ length lookup
        permissions = [
            ('can_publish', 'Can publish blog posts'),
        ]
    
    def __str__(self):
        return self.title


# ============ MODEL DEMO CÁC LOẠI INDEXES NÂNG CAO ============

class AdvancedIndexDemo(models.Model):
    """Model để demo tất cả các loại indexes từ Django documentation"""
    
    # Basic fields for indexing
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    category = models.CharField(max_length=50)
    
    # Numeric fields
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(default=0.0)
    views = models.PositiveIntegerField(default=0)
    
    # Date fields
    published_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    
    # JSON field for complex indexing
    metadata = models.JSONField(default=dict, blank=True)
    
    # Relations
    author = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='demo_items')
    
    class Meta:
        indexes = [
            # 1. Basic field indexes
            Index(fields=['title'], name='demo_title_idx'),
            Index(fields=['category'], name='demo_category_idx'),
            Index(fields=['slug'], name='demo_slug_idx'),
            
            # 2. Descending order indexes  
            Index(fields=['-created_at'], name='demo_created_desc_idx'),
            Index(fields=['-views'], name='demo_views_desc_idx'),
            Index(fields=['-rating'], name='demo_rating_desc_idx'),
            
            # 3. Composite indexes
            Index(fields=['category', 'is_active'], name='demo_cat_active_idx'),
            Index(fields=['author', '-created_at'], name='demo_author_date_idx'),
            Index(fields=['is_featured', 'is_active', '-rating'], name='demo_featured_idx'),
            
            # 4. Mixed ordering composite indexes
            Index(fields=['category', '-published_date', 'title'], name='demo_cat_pub_title_idx'),
            Index(fields=['-rating', 'price'], name='demo_rating_price_idx'),
            
            # 5. Functional indexes using expressions
            Index(Lower('title'), name='demo_lower_title_idx'),
            Index(Upper('category'), name='demo_upper_category_idx'),
            Index(F('price') * F('rating'), name='demo_price_rating_calc_idx'),
            Index(Round('rating'), name='demo_rating_rounded_idx'),
            
            # 6. Partial indexes with conditions
            Index(fields=['title'], condition=Q(is_active=True), name='demo_active_title_idx'),
            Index(fields=['price'], condition=Q(is_premium=True), name='demo_premium_price_idx'),
            Index(fields=['-created_at'], condition=Q(is_featured=True), name='demo_featured_recent_idx'),
            Index(fields=['rating'], condition=Q(rating__gte=4.0), name='demo_high_rating_idx'),
            Index(fields=['views'], condition=Q(is_active=True, is_featured=True), name='demo_active_featured_views_idx'),
            
            # 7. Complex condition indexes
            Index(fields=['category', 'price'], 
                  condition=Q(is_active=True) & Q(published_date__isnull=False), 
                  name='demo_active_published_idx'),
            Index(fields=['-created_at'], 
                  condition=Q(is_premium=True) | Q(is_featured=True), 
                  name='demo_special_items_idx'),
            
            # 8. Date-based partial indexes
            Index(fields=['title'], 
                  condition=Q(published_date__year=2024), 
                  name='demo_2024_title_idx'),
            Index(fields=['author'], 
                  condition=Q(created_at__gte=datetime(2024, 1, 1)), 
                  name='demo_recent_author_idx'),
            
            # 9. Covering indexes (PostgreSQL only, ignored on other DBs)
            Index(fields=['category'], include=['title', 'price'], name='demo_covering_idx'),
            Index(fields=['author'], include=['title', 'rating', 'views'], name='demo_author_covering_idx'),
            
            # 10. Multiple expression indexes
            Index(Lower('title'), Upper('category'), name='demo_title_cat_funcs_idx'),
            Index(F('views') + F('rating'), F('price') / 100, name='demo_calc_expressions_idx'),
        ]
        
        # Ordering for default queries
        ordering = ['-created_at', '-rating']
        
        verbose_name = "Advanced Index Demo"
        verbose_name_plural = "Advanced Index Demos"
    
    def __str__(self):
        return f"{self.title} ({self.category})"
    
    @property
    def popularity_score(self):
        """Calculate popularity based on views and rating"""
        return (self.views * 0.1) + (self.rating * 20)


# Model để demo index patterns trong real-world scenarios
class SearchableContent(models.Model):
    """Model optimized cho search và filtering performance"""
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.CharField(max_length=500)  # Comma-separated tags
    
    # Search optimization fields
    search_vector = models.TextField(blank=True)  # Pre-computed search text
    
    # Categorization
    primary_category = models.CharField(max_length=100)
    secondary_category = models.CharField(max_length=100, blank=True)
    
    # Metrics for ranking
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    
    # Temporal fields
    published_at = models.DateTimeField(null=True, blank=True)
    featured_until = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
        ('featured', 'Featured'),
    ], default='draft')
    
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
    
    class Meta:
        indexes = [
            # Search optimization indexes
            Index(fields=['search_vector'], name='search_vector_idx'),
            Index(fields=['title'], name='search_title_idx'),
            Index(Lower('title'), name='search_title_lower_idx'),
            
            # Category navigation indexes
            Index(fields=['primary_category', 'status'], name='search_cat_status_idx'),
            Index(fields=['primary_category', '-published_at'], name='search_cat_date_idx'),
            Index(fields=['secondary_category'], condition=Q(secondary_category__gt=''), name='search_subcat_idx'),
            
            # Performance ranking indexes
            Index(fields=['-view_count'], name='search_popular_idx'),
            Index(fields=['-like_count'], name='search_liked_idx'),
            Index(F('view_count') + F('like_count') * 2, name='search_engagement_idx'),
            
            # Status-based indexes
            Index(fields=['status', '-published_at'], name='search_status_date_idx'),
            Index(fields=['-published_at'], condition=Q(status='published'), name='search_published_recent_idx'),
            Index(fields=['-featured_until'], condition=Q(status='featured'), name='search_featured_idx'),
            
            # Author performance indexes
            Index(fields=['author', '-published_at'], name='search_author_date_idx'),
            Index(fields=['author'], condition=Q(status='published'), name='search_author_published_idx'),
            
            # Complex search scenarios
            Index(fields=['primary_category', '-view_count'], 
                  condition=Q(status='published', published_at__isnull=False), 
                  name='search_cat_popular_idx'),
            Index(fields=['-published_at'], 
                  condition=Q(status__in=['published', 'featured']), 
                  name='search_public_recent_idx'),
        ]
        
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title


# Model để demo GIN, GiST và SP-GiST indexes (PostgreSQL only)
class FullTextSearchDemo(models.Model):
    """Model để demo full-text search indexes và advanced PostgreSQL features"""
    
    title = models.CharField(max_length=300)
    content = models.TextField()
    summary = models.TextField(blank=True)
    
    # Array fields (PostgreSQL)
    keywords = models.JSONField(default=list)  # List of keywords
    categories = models.JSONField(default=list)  # Multiple categories
    
    # Geographic data simulation
    location_data = models.JSONField(default=dict)  # Store lat/lng as JSON
    
    # Full-text search vectors (would be TSVectorField in PostgreSQL)
    search_title = models.TextField(blank=True)
    search_content = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=10, default='en')
    
    class Meta:
        indexes = [
            # Basic text indexes
            Index(fields=['title'], name='fts_title_idx'),
            Index(fields=['language'], name='fts_language_idx'),
            
            # Functional indexes for text processing
            Index(Lower('title'), name='fts_title_lower_idx'),
            Index(Length('content'), name='fts_content_length_idx'),
            
            # JSON field indexes (PostgreSQL would use GIN)
            Index(fields=['keywords'], name='fts_keywords_idx'),
            Index(fields=['categories'], name='fts_categories_idx'),
            Index(fields=['location_data'], name='fts_location_idx'),
            
            # Multi-column text search
            Index(fields=['title', 'language'], name='fts_title_lang_idx'),
            Index(fields=['search_title'], name='fts_search_title_idx'),
            Index(fields=['search_content'], name='fts_search_content_idx'),
            
            # Performance indexes
            Index(fields=['-created_at'], name='fts_created_desc_idx'),
            Index(fields=['language', '-created_at'], name='fts_lang_date_idx'),
            
            # Conditional indexes for different languages
            Index(fields=['title'], condition=Q(language='en'), name='fts_english_title_idx'),
            Index(fields=['title'], condition=Q(language='vi'), name='fts_vietnamese_title_idx'),
            
            # Complex search combinations
            Index(fields=['language', 'title'], 
                  condition=Q(content__isnull=False), 
                  name='fts_lang_title_content_idx'),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.language})"


# ============ DEMO UNIQUE INDEXES VÀ CONDITIONAL UNIQUE CONSTRAINTS ============

class UniqueIndexDemo(models.Model):
    """Demo unique indexes và conditional unique constraints"""
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    slug = models.SlugField(max_length=100)
    
    # Multi-tenant data
    tenant_id = models.PositiveIntegerField()
    
    # Soft delete pattern
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ], default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            # Basic unique scenarios
            Index(fields=['name'], name='unique_name_idx'),
            Index(fields=['email'], name='unique_email_idx'),
            Index(fields=['slug'], name='unique_slug_idx'),
            
            # Multi-tenant unique constraints using partial indexes
            Index(fields=['email'], condition=Q(is_deleted=False), name='unique_active_email_idx'),
            Index(fields=['name', 'tenant_id'], condition=Q(is_deleted=False), name='unique_tenant_name_idx'),
            Index(fields=['slug', 'tenant_id'], name='unique_tenant_slug_idx'),
            
            # Conditional unique based on status
            Index(fields=['email'], condition=Q(status='active'), name='unique_active_user_email_idx'),
            Index(fields=['name'], condition=Q(status__in=['active', 'pending']), name='unique_live_user_name_idx'),
            
            # Performance indexes for common queries
            Index(fields=['tenant_id', '-created_at'], name='unique_tenant_created_idx'),
            Index(fields=['status', 'tenant_id'], name='unique_status_tenant_idx'),
            Index(fields=['-created_at'], condition=Q(is_deleted=False), name='unique_active_recent_idx'),
        ]
        
        # Note: SQLite không support partial unique constraints,
        # nhưng PostgreSQL và nhiều DB khác hỗ trợ
        constraints = [
            # Unique constraint cho active users trong cùng tenant
            models.UniqueConstraint(
                fields=['email', 'tenant_id'],
                condition=Q(is_deleted=False),
                name='unique_active_email_per_tenant'
            ),
            # Unique slug per tenant
            models.UniqueConstraint(
                fields=['slug', 'tenant_id'],
                name='unique_slug_per_tenant'
            ),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.tenant_id})"


# ============ DEMO PERFORMANCE OPTIMIZATION INDEXES ============

class PerformanceOptimizedModel(models.Model):
    """Model được thiết kế cho performance với strategic indexing"""
    
    # Identification
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    external_id = models.CharField(max_length=100, unique=True)
    
    # Core data
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(max_length=500, blank=True)
    
    # Categorization with hierarchy
    main_category = models.CharField(max_length=50)
    sub_category = models.CharField(max_length=50, blank=True)
    tags = models.JSONField(default=list)
    
    # Metrics for sorting/filtering
    popularity_score = models.FloatField(default=0.0)
    quality_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    engagement_count = models.PositiveIntegerField(default=0)
    
    # Temporal data
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    # Status and flags
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    
    # Relations
    owner = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='optimized_content')
    
    class Meta:
        indexes = [
            # === PRIMARY LOOKUP INDEXES ===
            Index(fields=['uuid'], name='perf_uuid_idx'),
            Index(fields=['external_id'], name='perf_external_id_idx'),
            
            # === CATEGORY NAVIGATION INDEXES ===
            Index(fields=['main_category'], name='perf_main_cat_idx'),
            Index(fields=['main_category', 'sub_category'], name='perf_cat_subcat_idx'),
            Index(fields=['sub_category'], condition=Q(sub_category__gt=''), name='perf_subcat_idx'),
            
            # === PUBLISHED CONTENT INDEXES ===
            # Most common query: get published content by category, ordered by date
            Index(fields=['main_category', '-published_at'], 
                  condition=Q(is_published=True), 
                  name='perf_published_cat_date_idx'),
            
            # Featured content by category
            Index(fields=['main_category', '-published_at'], 
                  condition=Q(is_published=True, is_featured=True), 
                  name='perf_featured_cat_date_idx'),
            
            # === RANKING AND SORTING INDEXES ===
            # Sort by popularity within categories
            Index(fields=['main_category', '-popularity_score'], 
                  condition=Q(is_published=True), 
                  name='perf_cat_popularity_idx'),
            
            # Sort by quality rating
            Index(fields=['-quality_rating'], 
                  condition=Q(is_published=True), 
                  name='perf_quality_idx'),
            
            # Combined scoring index
            Index(F('popularity_score') + F('quality_rating'), 
                  name='perf_combined_score_idx'),
            
            # === TIME-BASED INDEXES ===
            # Recent content
            Index(fields=['-published_at'], 
                  condition=Q(is_published=True), 
                  name='perf_recent_published_idx'),
            
            # Trending content (time-sensitive)
            Index(fields=['-published_at'], 
                  condition=Q(is_trending=True, is_published=True), 
                  name='perf_trending_idx'),
            
            # Content expiration management
            Index(fields=['expires_at'], 
                  condition=Q(expires_at__isnull=False), 
                  name='perf_expiring_idx'),
            
            # === PREMIUM CONTENT INDEXES ===
            Index(fields=['main_category', '-published_at'], 
                  condition=Q(is_premium=True, is_published=True), 
                  name='perf_premium_cat_idx'),
            
            # === AUTHOR PERFORMANCE INDEXES ===
            Index(fields=['owner', '-published_at'], name='perf_author_date_idx'),
            Index(fields=['owner'], 
                  condition=Q(is_published=True), 
                  name='perf_author_published_idx'),
            
            # === FULL-TEXT SEARCH PREPARATION ===
            Index(fields=['title'], name='perf_title_search_idx'),
            Index(Lower('title'), name='perf_title_lower_idx'),
            Index(fields=['main_category', 'title'], name='perf_cat_title_idx'),
            
            # === ADMIN AND MANAGEMENT INDEXES ===
            Index(fields=['is_published', '-last_modified'], name='perf_status_modified_idx'),
            Index(fields=['-last_modified'], 
                  condition=Q(is_published=False), 
                  name='perf_draft_modified_idx'),
            
            # === JSON FIELD INDEXES (cho PostgreSQL) ===
            Index(fields=['tags'], name='perf_tags_idx'),
            
            # === COVERING INDEXES cho common read patterns ===
            Index(fields=['main_category'], 
                  include=['title', 'published_at', 'popularity_score'], 
                  name='perf_cat_covering_idx'),
            Index(fields=['owner'], 
                  include=['title', 'main_category', 'published_at'], 
                  name='perf_author_covering_idx'),
        ]
        
        # Default ordering optimized cho most common use case
        ordering = ['-published_at', '-popularity_score']
        
        constraints = [
            # Business rules
            models.CheckConstraint(
                check=Q(quality_rating__gte=0) & Q(quality_rating__lte=5),
                name='perf_valid_quality_rating'
            ),
            models.CheckConstraint(
                check=Q(popularity_score__gte=0),
                name='perf_valid_popularity_score'
            ),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.main_category})"
    
    @property
    def is_expired(self):
        """Check if content has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


# ============ DEMO TẤT CẢ CÁC META OPTIONS ============

# 1. ABSTRACT BASE CLASS
class AbstractBaseDemo(models.Model):
    """Abstract base class demo"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True  # Không tạo table
        ordering = ['-created_at']
        get_latest_by = 'created_at'


# 2. APP_LABEL DEMO
class AppLabelDemo(models.Model):
    """Model defined outside normal app structure"""
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'myapp'  # Explicit app declaration
        verbose_name = "App Label Demo"


# 3. DB_TABLE và DB_TABLE_COMMENT
class CustomTableDemo(models.Model):
    """Demo custom table name và comment"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    class Meta:
        db_table = 'custom_content_table'  # Custom table name
        db_table_comment = "Custom table for storing content with specific naming"
        verbose_name = "Custom Table Demo"
        verbose_name_plural = "Custom Table Demos"


# 4. MANAGED FALSE - Database View simulation
class UnmanagedDemo(models.Model):
    """Unmanaged model - represents existing DB view/table"""
    view_id = models.IntegerField(primary_key=True)
    calculated_value = models.DecimalField(max_digits=10, decimal_places=2)
    source_table = models.CharField(max_length=100)
    
    class Meta:
        managed = False  # Django won't create/delete this table
        db_table = 'calculation_view'
        verbose_name = "Unmanaged Demo View"


# 5. DEFAULT_RELATED_NAME
class CategoryDemo(models.Model):
    """Category with custom related name pattern"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        default_related_name = '%(app_label)s_%(model_name)s_items'
        verbose_name_plural = "Category Demos"


class CategoryItemDemo(models.Model):
    """Items belonging to category"""
    category = models.ForeignKey(CategoryDemo, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    # Related name will be: myapp_categoryitemdemo_items


# 6. GET_LATEST_BY variations
class LatestByDemo(models.Model):
    """Demo get_latest_by options"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField()
    priority = models.IntegerField(default=1)
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        # Single field
        get_latest_by = 'published_date'
        ordering = ['-published_date']


class MultiLatestByDemo(models.Model):
    """Demo multiple fields for get_latest_by"""
    title = models.CharField(max_length=200)
    published_date = models.DateTimeField()
    priority = models.IntegerField(default=1)
    
    class Meta:
        # Multiple fields: priority descending, then date ascending
        get_latest_by = ['-priority', 'published_date']


# 7. ORDER_WITH_RESPECT_TO
class QuestionDemo(models.Model):
    """Question model for ordered answers"""
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class AnswerDemo(models.Model):
    """Answers ordered with respect to question"""
    question = models.ForeignKey(QuestionDemo, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    
    class Meta:
        order_with_respect_to = 'question'  # Adds _order field automatically


# 8. PERMISSIONS và DEFAULT_PERMISSIONS
class PermissionsDemo(models.Model):
    """Model with custom permissions"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    classification_level = models.CharField(max_length=20, choices=[
        ('public', 'Public'),
        ('confidential', 'Confidential'),
        ('secret', 'Secret'),
        ('top_secret', 'Top Secret'),
    ])
    
    class Meta:
        permissions = [
            ('can_view_confidential', 'Can view confidential documents'),
            ('can_view_secret', 'Can view secret documents'),
            ('can_view_top_secret', 'Can view top secret documents'),
            ('can_declassify', 'Can declassify documents'),
            ('can_export', 'Can export documents'),
        ]
        default_permissions = ('add', 'change', 'delete', 'view')


class NoPermissionsDemo(models.Model):
    """Model with no default permissions"""
    data = models.TextField()
    
    class Meta:
        default_permissions = ()  # No default permissions


# 9. PROXY MODEL
class ProxyBaseDemo(models.Model):
    """Base person model"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    birth_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']


class ActiveProxyDemo(ProxyBaseDemo):
    """Proxy model for active persons only"""
    
    class Meta:
        proxy = True  # Same table as ProxyBaseDemo
        verbose_name = "Active Person Demo"
        verbose_name_plural = "Active Person Demos"


# 10. REQUIRED_DB_FEATURES và REQUIRED_DB_VENDOR
class DBFeaturesDemo(models.Model):
    """Model requiring specific DB features"""
    name = models.CharField(max_length=100)
    location_data = models.JSONField(default=dict)
    
    class Meta:
        required_db_features = ['supports_json_field']
        verbose_name = "DB Features Demo"


class DBVendorDemo(models.Model):
    """Model specific to certain database vendor"""
    jsonb_data = models.JSONField()
    array_data = models.JSONField(default=list)
    
    class Meta:
        required_db_vendor = 'postgresql'  # Only on PostgreSQL
        verbose_name = "PostgreSQL Specific Demo"


# 11. SELECT_ON_SAVE
class SelectOnSaveDemo(models.Model):
    """Model using legacy save algorithm"""
    name = models.CharField(max_length=100)
    data = models.TextField()
    
    class Meta:
        select_on_save = True  # Use pre-1.6 save algorithm


# 12. UNIQUE_TOGETHER (deprecated but still supported)
class UniqueTogetherDemo(models.Model):
    """Demo legacy unique_together"""
    driver = models.CharField(max_length=100)
    restaurant = models.CharField(max_length=100)
    shift_date = models.DateField()
    
    class Meta:
        unique_together = [
            ['driver', 'restaurant'],  # Driver unique per restaurant
            ['driver', 'shift_date'],  # Driver unique per date
        ]


# 13. TABLESPACE DEMO
class TablespaceDemo(models.Model):
    """Demo tablespace configuration"""
    large_data = models.TextField()
    binary_data = models.BinaryField()
    
    class Meta:
        db_tablespace = 'large_data_space'  # Custom tablespace
        verbose_name = "Tablespace Demo"


# 14. COMPREHENSIVE META OPTIONS DEMO
class ComprehensiveMetaDemo(AbstractBaseDemo):
    """Model demonstrating multiple Meta options together"""
    
    # Fields
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ], default='draft')
    
    # Relations
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
    category = models.ForeignKey(CategoryDemo, on_delete=models.CASCADE)
    
    # Metrics
    view_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    # Dates
    published_at = models.DateTimeField(null=True, blank=True)
    featured_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        # Table configuration
        db_table = 'comprehensive_meta_demo'
        db_table_comment = 'Comprehensive demonstration of Django Meta options'
        
        # Ordering and retrieval
        ordering = ['-published_at', '-created_at', 'title']
        get_latest_by = ['published_at', '-created_at']
        
        # Constraints and indexes
        indexes = [
            Index(fields=['status', '-published_at'], name='meta_status_pub_idx'),
            Index(fields=['author', '-created_at'], name='meta_author_created_idx'),
            Index(fields=['category', 'status'], name='meta_cat_status_idx'),
            Index(fields=['-view_count'], name='meta_popular_idx'),
            Index(fields=['slug'], name='meta_slug_idx'),
            # Partial indexes
            Index(fields=['-published_at'], 
                  condition=Q(status='published'), 
                  name='meta_published_date_idx'),
            Index(fields=['rating'], 
                  condition=Q(status='published', rating__gte=4.0), 
                  name='meta_high_rated_idx'),
        ]
        
        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'category'],
                name='meta_unique_slug_per_category'
            ),
            models.CheckConstraint(
                condition=Q(rating__gte=0) & Q(rating__lte=5),
                name='meta_valid_rating_range'
            ),
            models.CheckConstraint(
                condition=Q(view_count__gte=0),
                name='meta_positive_view_count'
            ),
        ]
        
        # Permissions
        permissions = [
            ('can_feature_meta', 'Can feature meta content'),
            ('can_publish_meta', 'Can publish meta content'),
            ('can_moderate_meta', 'Can moderate meta content'),
            ('can_view_meta_analytics', 'Can view meta analytics'),
        ]
        
        # Display names
        verbose_name = 'Comprehensive Meta Demo'
        verbose_name_plural = 'Comprehensive Meta Demos'
        
        # Related names
        default_related_name = 'meta_%(class)s_set'
    
    def __str__(self):
        return f"{self.title} ({self.status})"


# 15. MANAGER CONFIGURATION DEMO
class PublishedManager(models.Manager):
    """Custom manager for published items"""
    
    def get_queryset(self):
        return super().get_queryset().filter(status='published')
    
    def featured(self):
        return self.filter(
            featured_until__isnull=False,
            featured_until__gte=timezone.now()
        )


class ManagerDemo(models.Model):
    """Demo custom manager configuration"""
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
    ], default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    featured_until = models.DateTimeField(null=True, blank=True)
    
    # Managers
    objects = models.Manager()  # Default manager
    published = PublishedManager()  # Custom manager
    
    class Meta:
        base_manager_name = 'objects'  # Manager for relations
        default_manager_name = 'published'  # Manager for admin, etc.
        ordering = ['-published_at']
        verbose_name = "Manager Demo"
        verbose_name_plural = "Manager Demos"
    
    def __str__(self):
        return self.title
