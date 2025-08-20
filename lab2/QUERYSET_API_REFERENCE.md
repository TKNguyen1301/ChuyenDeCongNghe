# Django QuerySet API Quick Reference Guide

**Based on Django 5.2 Official Documentation**  
**URL**: https://docs.djangoproject.com/en/5.2/ref/models/querysets/

## 📚 Table of Contents

1. [QuerySet Evaluation](#queryset-evaluation)
2. [Methods Returning QuerySets](#methods-returning-querysets)
3. [Methods NOT Returning QuerySets](#methods-not-returning-querysets)
4. [Field Lookups](#field-lookups)
5. [Aggregation Functions](#aggregation-functions)
6. [Query Tools](#query-tools)
7. [Optimization Techniques](#optimization-techniques)
8. [Performance Tips](#performance-tips)

---

## 🔄 QuerySet Evaluation

**QuerySets are LAZY** - they don't hit the database until evaluated.

### Evaluation Triggers:
```python
# These operations evaluate the QuerySet:
for item in queryset:          # Iteration
bool(queryset)                 # Boolean context
len(queryset)                  # Length
list(queryset)                 # List conversion
repr(queryset)                 # String representation
queryset[0]                    # Indexing
queryset[5:10]                 # Slicing (returns list)
queryset[::2]                  # Slicing with step

# These DON'T evaluate (return new QuerySet):
queryset[5:10]                 # Slicing without step
queryset.filter(...)           # Further filtering
queryset.order_by(...)         # Ordering
```

### Caching Behavior:
```python
# QuerySet results are cached after first evaluation
qs = Entry.objects.filter(rating=5)
list(qs)  # Hits database, caches results
list(qs)  # Uses cache, no database hit

# Force fresh query
qs.all()  # Returns new QuerySet
```

---

## 🔄 Methods Returning QuerySets

### 🔍 Filtering Methods
```python
# filter() - Include matching records
Entry.objects.filter(rating__gte=4)
Entry.objects.filter(blog__name='Tech', rating=5)

# exclude() - Exclude matching records  
Entry.objects.exclude(rating__lt=3)
Entry.objects.exclude(headline__icontains='test')

# none() - Return empty QuerySet
Entry.objects.none()

# all() - Return copy of QuerySet
Entry.objects.all()
```

### ➕ Annotation Methods
```python
# annotate() - Add calculated fields
Entry.objects.annotate(
    engagement=F('comments') + F('pingbacks'),
    is_popular=Case(When(rating__gte=4, then=True), default=False),
    author_count=Count('authors')
)

# alias() - Add expressions without selecting them
Entry.objects.alias(
    engagement=F('comments') + F('pingbacks')
).filter(engagement__gt=20)
```

### 📊 Ordering and Grouping
```python
# order_by() - Sort results
Entry.objects.order_by('rating', '-pub_date')
Entry.objects.order_by('?')  # Random order
Entry.objects.order_by(F('rating').desc())  # Expression ordering

# reverse() - Reverse current ordering
Entry.objects.order_by('rating').reverse()

# distinct() - Remove duplicates
Author.objects.filter(entry__isnull=False).distinct()
Entry.objects.order_by('blog').distinct('blog')  # PostgreSQL only
```

### 📋 Value Selection
```python
# values() - Return dictionaries
Entry.objects.values('headline', 'rating', 'blog__name')

# values_list() - Return tuples
Entry.objects.values_list('headline', 'rating')
Entry.objects.values_list('rating', flat=True)  # Single values

# only() - Load only specific fields
Entry.objects.only('headline', 'rating')

# defer() - Don't load specific fields
Entry.objects.defer('body_text')
```

### 📅 Date/Time Methods
```python
# dates() - Get unique dates
Entry.objects.dates('pub_date', 'year')
Entry.objects.dates('pub_date', 'month', order='DESC')

# datetimes() - Get unique datetimes
Entry.objects.datetimes('created', 'day')
```

### 🔗 Relationship Optimization
```python
# select_related() - ForeignKey/OneToOne (SQL JOIN)
Entry.objects.select_related('blog', 'blog__category')

# prefetch_related() - ManyToMany/Reverse FK (separate queries)
Entry.objects.prefetch_related('authors', 'tags')

# Custom prefetch
Prefetch('authors', queryset=Author.objects.filter(active=True))
```

### 🔧 Advanced Methods
```python
# extra() - Add custom SQL
Entry.objects.extra(
    select={'is_recent': "pub_date > '2024-01-01'"},
    where=["rating >= %s"],
    params=[4]
)

# raw() - Execute raw SQL
Entry.objects.raw("SELECT * FROM app_entry WHERE rating >= %s", [4])

# using() - Specify database
Entry.objects.using('replica_db')

# select_for_update() - Row locking
Entry.objects.select_for_update().filter(rating=5)
```

### 🔀 Set Operations
```python
# union() - Combine QuerySets (OR)
qs1.union(qs2, all=True)  # Include duplicates

# intersection() - Common records (AND)
qs1.intersection(qs2)

# difference() - Records in first but not second
qs1.difference(qs2)
```

---

## ❌ Methods NOT Returning QuerySets

### 🎯 Single Object Retrieval
```python
# get() - Get single object (raises exceptions)
Entry.objects.get(pk=1)
Entry.objects.get(headline='Unique Title')

# first() - First object or None
Entry.objects.filter(rating=5).first()

# last() - Last object or None  
Entry.objects.order_by('pub_date').last()

# latest() / earliest() - By field
Entry.objects.latest('pub_date')
Entry.objects.earliest('created')
```

### ➕ Object Creation
```python
# create() - Create and save object
Entry.objects.create(
    headline='New Entry',
    blog=blog,
    rating=4
)

# get_or_create() - Get existing or create new
obj, created = Entry.objects.get_or_create(
    headline='Unique Entry',
    defaults={'rating': 4, 'blog': blog}
)

# update_or_create() - Update existing or create new
obj, created = Entry.objects.update_or_create(
    headline='Entry to Update',
    defaults={'rating': 5, 'updated': timezone.now()}
)
```

### 📦 Bulk Operations
```python
# bulk_create() - Create multiple objects efficiently
entries = [Entry(headline=f'Entry {i}') for i in range(100)]
Entry.objects.bulk_create(entries, batch_size=1000)

# bulk_update() - Update multiple objects
Entry.objects.bulk_update(entries, ['rating'], batch_size=1000)

# update() - Update matching records
Entry.objects.filter(rating__lt=3).update(
    rating=3,
    updated=timezone.now()
)

# delete() - Delete matching records
Entry.objects.filter(rating=1).delete()
```

### 📊 Information Methods
```python
# count() - Count records
Entry.objects.filter(rating__gte=4).count()

# exists() - Check if any records exist
Entry.objects.filter(rating=5).exists()

# contains() - Check if object is in QuerySet
Entry.objects.filter(rating__gte=4).contains(entry)

# aggregate() - Calculate statistics
Entry.objects.aggregate(
    total=Count('id'),
    avg_rating=Avg('rating'),
    max_comments=Max('comments')
)
```

### 🔄 Iteration Methods
```python
# iterator() - Memory-efficient iteration
for entry in Entry.objects.iterator(chunk_size=1000):
    process(entry)

# in_bulk() - Get multiple objects by key
Entry.objects.in_bulk([1, 2, 3])  # By primary key
Entry.objects.in_bulk(['title1', 'title2'], field_name='headline')
```

### 📝 Explanation
```python
# explain() - Show query execution plan
Entry.objects.filter(rating__gte=4).explain()
Entry.objects.select_related('blog').explain(analyze=True)
```

---

## 🔍 Field Lookups

### 🎯 Exact Matches
```python
Entry.objects.filter(rating__exact=5)      # Exact match
Entry.objects.filter(headline__iexact='title')  # Case-insensitive
```

### 📝 String Operations
```python
# Contains
Entry.objects.filter(headline__contains='Django')
Entry.objects.filter(headline__icontains='DJANGO')  # Case-insensitive

# Starts/Ends with
Entry.objects.filter(headline__startswith='Django')
Entry.objects.filter(headline__istartswith='DJANGO')
Entry.objects.filter(headline__endswith='Tutorial') 
Entry.objects.filter(headline__iendswith='TUTORIAL')
```

### 🔢 Comparisons
```python
Entry.objects.filter(rating__gt=3)         # Greater than
Entry.objects.filter(rating__gte=4)        # Greater than or equal
Entry.objects.filter(rating__lt=3)         # Less than
Entry.objects.filter(rating__lte=2)        # Less than or equal
```

### 📋 Lists and Ranges
```python
Entry.objects.filter(rating__in=[4, 5])           # In list
Entry.objects.filter(rating__range=(3, 5))        # Between (inclusive)
Entry.objects.filter(pub_date__range=(start, end)) # Date range
```

### 📅 Date/Time Lookups
```python
# Date components
Entry.objects.filter(pub_date__year=2024)
Entry.objects.filter(pub_date__month=6)
Entry.objects.filter(pub_date__day=15)
Entry.objects.filter(pub_date__week=25)
Entry.objects.filter(pub_date__week_day=2)     # Sunday=1, Monday=2
Entry.objects.filter(pub_date__iso_week_day=1)  # Monday=1, Sunday=7
Entry.objects.filter(pub_date__quarter=2)

# Time components  
Entry.objects.filter(created__hour=14)
Entry.objects.filter(created__minute=30)
Entry.objects.filter(created__second=0)

# Date without time
Entry.objects.filter(created__date=date(2024, 6, 15))
Entry.objects.filter(created__time=time(14, 30))
```

### ❓ Null Checks
```python
Entry.objects.filter(headline__isnull=True)   # IS NULL
Entry.objects.filter(headline__isnull=False)  # IS NOT NULL
```

### 🔍 Regular Expressions
```python
Entry.objects.filter(headline__regex=r'^Entry \d+')     # Case-sensitive
Entry.objects.filter(headline__iregex=r'^entry \d+')    # Case-insensitive
```

### 🗂️ JSON Field Lookups
```python
# Key existence
Product.objects.filter(data__has_key='color')

# Key value
Product.objects.filter(data__color='red')

# Nested keys
Product.objects.filter(data__specs__weight=100)

# JSON path (PostgreSQL)
Product.objects.filter(data__0__name='first_item')
```

---

## 📊 Aggregation Functions

### Basic Aggregations
```python
from django.db.models import Avg, Count, Max, Min, Sum, StdDev, Variance

# Single aggregations
Entry.objects.aggregate(
    total=Count('id'),
    avg_rating=Avg('rating'),
    max_rating=Max('rating'), 
    min_rating=Min('rating'),
    total_comments=Sum('comments'),
    rating_stddev=StdDev('rating'),
    rating_variance=Variance('rating')
)
```

### Grouped Aggregations
```python
# Group by model (annotate)
Blog.objects.annotate(
    entry_count=Count('entry'),
    avg_rating=Avg('entry__rating'),
    latest_entry=Max('entry__pub_date')
)
```

### Conditional Aggregations
```python
# With filter
Entry.objects.aggregate(
    high_rated_count=Count('id', filter=Q(rating__gte=4)),
    avg_high_rating=Avg('rating', filter=Q(rating__gte=4))
)

# With distinct
Entry.objects.aggregate(
    unique_ratings=Count('rating', distinct=True)
)

# With default values
Entry.objects.aggregate(
    avg_rating=Avg('rating', default=0)
)
```

---

## 🔧 Query Tools

### Q Objects (Complex Queries)
```python
from django.db.models import Q

# Basic Q objects
Q(rating__gte=4)
Q(headline__icontains='django')

# Logical operations
Q(rating__gte=4) & Q(blog__name='Tech')  # AND
Q(rating__gte=4) | Q(comments__gte=100)  # OR
~Q(headline__icontains='test')           # NOT
Q(rating=5) ^ Q(comments__gte=50)        # XOR

# Complex combinations
(Q(rating__gte=4) | Q(comments__gte=100)) & ~Q(headline__icontains='test')
```

### F Objects (Field References)
```python
from django.db.models import F

# Field comparisons
Entry.objects.filter(comments__gt=F('pingbacks'))

# Arithmetic operations
Entry.objects.filter(rating__gt=F('comments') / 10)
Entry.objects.annotate(engagement=F('comments') + F('pingbacks'))

# Updates with F expressions
Entry.objects.update(comments=F('comments') + 1)
```

### Prefetch Objects
```python
from django.db.models import Prefetch

# Custom prefetch with filtering
Prefetch(
    'entries',
    queryset=Entry.objects.filter(rating__gte=4),
    to_attr='high_rated_entries'
)

# Multiple prefetch levels
Prefetch(
    'entries__authors',
    queryset=Author.objects.select_related('profile')
)
```

### FilteredRelation
```python
from django.db.models import FilteredRelation

# Filtered annotations on relations
Blog.objects.annotate(
    high_rated_entries=FilteredRelation(
        'entries',
        condition=Q(entries__rating__gte=4)
    )
).annotate(
    high_rated_count=Count('high_rated_entries')
)
```

---

## ⚡ Optimization Techniques

### 🔗 Relationship Loading
```python
# Bad: N+1 queries
for entry in Entry.objects.all():
    print(entry.blog.name)  # Hits DB for each entry

# Good: Use select_related for ForeignKey
for entry in Entry.objects.select_related('blog'):
    print(entry.blog.name)  # Single query with JOIN

# Good: Use prefetch_related for ManyToMany
for entry in Entry.objects.prefetch_related('authors'):
    for author in entry.authors.all():  # No additional queries
        print(author.name)
```

### 📋 Field Selection
```python
# Load only needed fields
Entry.objects.only('headline', 'rating')

# Exclude large fields
Entry.objects.defer('body_text')

# Combine with relationships
Entry.objects.select_related('blog').only(
    'headline', 'rating', 'blog__name'
)
```

### 📦 Bulk Operations
```python
# Bulk create (faster than individual creates)
entries = [Entry(headline=f'Entry {i}') for i in range(1000)]
Entry.objects.bulk_create(entries, batch_size=100)

# Bulk update (faster than individual updates)
entries = Entry.objects.filter(rating__lt=3)
for entry in entries:
    entry.rating = 3
Entry.objects.bulk_update(entries, ['rating'], batch_size=100)

# Single query update
Entry.objects.filter(rating__lt=3).update(rating=3)
```

### 🔄 Memory Efficiency
```python
# Use iterator for large datasets
for entry in Entry.objects.iterator(chunk_size=1000):
    process_entry(entry)  # Process one at a time

# Use values() for simple data
for entry_data in Entry.objects.values('headline', 'rating'):
    process_data(entry_data)  # Lighter than full objects
```

---

## 📈 Performance Tips

### 🔍 Query Analysis
```python
# Show query execution plan
queryset.explain()
queryset.explain(analyze=True, buffers=True)

# Debug queries
from django.db import connection
print(connection.queries)  # Show all executed queries

# Profile complex queries
import time
start = time.time()
list(queryset)
print(f"Query took: {time.time() - start:.4f} seconds")
```

### 💾 Caching Strategies
```python
# QuerySet caching
qs = Entry.objects.filter(rating__gte=4)
list(qs)  # Caches results
list(qs)  # Uses cache

# Force fresh query
qs.all()  # New QuerySet, fresh query

# Conditional evaluation
if qs:  # Evaluates QuerySet
    process(qs)  # Uses cached results

# Better: Use exists() for checking existence
if qs.exists():  # Optimized existence check
    process(qs)
```

### 📊 Database Indexes
```python
# Add indexes in model Meta
class Entry(models.Model):
    headline = models.CharField(max_length=255)
    rating = models.IntegerField()
    pub_date = models.DateField()
    
    class Meta:
        indexes = [
            models.Index(fields=['rating']),
            models.Index(fields=['pub_date']),
            models.Index(fields=['rating', 'pub_date']),  # Composite
        ]
```

### 🎯 Query Optimization Patterns
```python
# Use count() instead of len()
Entry.objects.filter(rating=5).count()  # Efficient
# NOT: len(Entry.objects.filter(rating=5))  # Loads all objects

# Use exists() for boolean checks
Entry.objects.filter(rating=5).exists()  # Efficient
# NOT: bool(Entry.objects.filter(rating=5))  # Loads objects

# Use in_bulk() for multiple objects
Entry.objects.in_bulk([1, 2, 3, 4, 5])  # Single query
# NOT: [Entry.objects.get(pk=i) for i in [1,2,3,4,5]]  # 5 queries

# Use select_related chains efficiently
Entry.objects.select_related('blog__category__parent')  # Single JOIN query
```

---

## 🚀 Quick Command Reference

```python
# Most commonly used patterns
Entry.objects.all()
Entry.objects.filter(rating__gte=4)
Entry.objects.get(pk=1)
Entry.objects.create(headline='New Entry')
Entry.objects.filter(rating=5).count()
Entry.objects.filter(rating__gte=4).exists()
Entry.objects.order_by('-pub_date')[:10]
Entry.objects.select_related('blog').prefetch_related('authors')
Entry.objects.values('headline', 'rating')
Entry.objects.aggregate(avg_rating=Avg('rating'))
Entry.objects.filter(Q(rating=5) | Q(comments__gte=100))
```

---

**💡 Remember**: Start simple, optimize when needed, and always measure performance!
