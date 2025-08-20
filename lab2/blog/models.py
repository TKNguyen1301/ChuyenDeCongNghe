from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

# Basic Person model theo Django documentation
class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Musician model với ForeignKey relationship
class Musician(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    instrument = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Album model với many-to-one relationship
class Album(models.Model):
    artist = models.ForeignKey(Musician, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    release_date = models.DateField()
    num_stars = models.IntegerField()
    
    def __str__(self):
        return self.name

# Ví dụ về choices field với TextChoices
class Student(models.Model):
    class YearInSchool(models.TextChoices):
        FRESHMAN = 'FR', 'Freshman'
        SOPHOMORE = 'SO', 'Sophomore'
        JUNIOR = 'JR', 'Junior'
        SENIOR = 'SR', 'Senior'
        GRADUATE = 'GR', 'Graduate'
    
    name = models.CharField(max_length=100)
    year_in_school = models.CharField(
        max_length=2,
        choices=YearInSchool.choices,
        default=YearInSchool.FRESHMAN,
    )
    
    def __str__(self):
        return self.name
    
    def is_upperclass(self):
        return self.year_in_school in {
            self.YearInSchool.JUNIOR,
            self.YearInSchool.SENIOR,
        }

# Ví dụ về many-to-many relationship
class Topping(models.Model):
    name = models.CharField(max_length=30)
    
    def __str__(self):
        return self.name

class Pizza(models.Model):
    name = models.CharField(max_length=50)
    toppings = models.ManyToManyField(Topping)
    
    def __str__(self):
        return self.name

# Advanced Field Types Example Model
class AdvancedFieldExample(models.Model):
    """Model demonstrating various Django field types"""
    
    # ID field
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Text fields
    title = models.CharField(max_length=200, help_text="Short title")
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    # Email and URL fields
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Number fields
    integer_field = models.IntegerField(default=0)
    big_integer = models.BigIntegerField(default=0)
    small_integer = models.SmallIntegerField(default=0)
    positive_integer = models.PositiveIntegerField(default=0)
    positive_small_integer = models.PositiveSmallIntegerField(default=0)
    
    # Float and Decimal
    float_field = models.FloatField(default=0.0)
    decimal_field = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Boolean field
    is_active = models.BooleanField(default=True)
    
    # Date and Time fields
    date_field = models.DateField(auto_now_add=True)
    datetime_field = models.DateTimeField(auto_now=True)
    time_field = models.TimeField(null=True, blank=True)
    duration_field = models.DurationField(null=True, blank=True)
    
    # IP Address field
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # JSON field
    json_data = models.JSONField(default=dict, blank=True)
    
    # Binary field
    binary_data = models.BinaryField(blank=True)
    
    # File fields (commented out vì cần MEDIA settings)
    # file_field = models.FileField(upload_to='files/', blank=True)
    # image_field = models.ImageField(upload_to='images/', blank=True)
    
    # Choices with IntegerChoices
    class Priority(models.IntegerChoices):
        LOW = 1, 'Low'
        MEDIUM = 2, 'Medium'
        HIGH = 3, 'High'
        URGENT = 4, 'Urgent'
    
    priority = models.IntegerField(choices=Priority.choices, default=Priority.MEDIUM)
    
    # Field with validators
    score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        help_text="Score between 0 and 100"
    )
    
    class Meta:
        ordering = ['-datetime_field']
        verbose_name = "Advanced Field Example"
        verbose_name_plural = "Advanced Field Examples"
    
    def __str__(self):
        return self.title or str(self.id)

# Model with custom field options
class Product(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    sku = models.CharField(max_length=50, unique=True, db_column='product_sku')
    price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    created_date = models.DateField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    
    # Field với db_comment (Django 4.2+)
    notes = models.TextField(
        blank=True,
        db_comment="Internal notes about the product"
    )
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gt=0),
                name='positive_price'
            )
        ]
        indexes = [
            models.Index(fields=['name', 'is_available']),
        ]
    
    def __str__(self):
        return f"{self.name} (${self.price})"

# Model demonstrating field relationships
class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    authors = models.ManyToManyField(Author, related_name='books')
    publication_date = models.DateField()
    pages = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-publication_date']
        unique_together = ['title', 'publication_date']
    
    def __str__(self):
        return self.title

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['book', 'reviewer_name']
    
    def __str__(self):
        return f"{self.book.title} - {self.rating}/5"



from django.db import models

class MigrationPractice(models.Model):
    """Model for practicing migrations"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'migration_practice'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
