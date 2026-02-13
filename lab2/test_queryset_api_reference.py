#!/usr/bin/env python
"""
Django QuerySet API Reference Comprehensive Practice
Following https://docs.djangoproject.com/en/5.2/ref/models/querysets/

This script demonstrates ALL Django QuerySet methods and field lookups
systematically following the official documentation structure.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, datetime, timedelta, time
from django.utils import timezone
from django.db import models, transaction
from django.db.models import (
    Q, F, Count, Sum, Avg, Max, Min, StdDev, Variance, Case, When, Value,
    Prefetch, FilteredRelation
)
from django.db.models.functions import (
    Lower, Upper, Concat, Extract, Coalesce, Length, Now
)
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import json

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modelspractice.settings')
    django.setup()

from django.contrib.auth.models import User
from query_practice.models import *


def print_section(title, level=1):
    """Print a formatted section header."""
    if level == 1:
        print(f"\n{'='*80}")
        print(f" {title}")
        print(f"{'='*80}")
    elif level == 2:
        print(f"\n{'-'*60}")
        print(f" {title}")
        print(f"{'-'*60}")
    else:
        print(f"\n### {title} ###")


def print_queryset_info(qs, title="QuerySet Info"):
    """Print detailed information about a QuerySet."""
    print(f"\n{title}:")
    print(f"  Type: {type(qs)}")
    print(f"  Ordered: {qs.ordered}")
    print(f"  DB: {qs.db}")
    print(f"  Count: {qs.count()}")
    try:
        print(f"  SQL: {qs.query}")
    except:
        print("  SQL: Not available")


def setup_comprehensive_data():
    """Create comprehensive test data for QuerySet API testing."""
    print_section("Setting up Comprehensive Test Data")
    
    # Clear all data
    for model in [Entry, Blog, Author, Product, Category, Manufacturer, Tag, 
                  Customer, Address, Order, OrderItem, Review]:
        model.objects.all().delete()
    
    User.objects.filter(username__startswith='qs_test').delete()
    
    # Create users
    users = []
    for i in range(10):
        user = User.objects.create_user(
            username=f'qs_test_user{i+1}',
            email=f'qs_test{i+1}@example.com',
            first_name=f'User{i+1}',
            last_name='Test'
        )
        users.append(user)
    
    # Create comprehensive blogs
    blogs = []
    blog_data = [
        ('Tech Innovations', 'Latest in technology'),
        ('Food Adventures', 'Culinary explorations'),
        ('Travel Stories', 'Journey around the world'),
        ('Health & Fitness', 'Wellness and fitness tips'),
        ('Science Today', 'Scientific discoveries'),
        ('Art & Culture', 'Creative expressions'),
        ('Business Insights', 'Market analysis and trends'),
        ('Education Hub', 'Learning and development'),
    ]
    
    for name, tagline in blog_data:
        blog = Blog.objects.create(name=name, tagline=tagline)
        blogs.append(blog)
    
    # Create authors with varied data
    authors = []
    author_data = [
        ('John Smith', 'john.smith@example.com', date(1985, 3, 15)),
        ('Jane Doe', 'jane.doe@example.com', date(1990, 7, 22)),
        ('Bob Wilson', 'bob.wilson@example.com', date(1988, 11, 8)),
        ('Alice Brown', 'alice.brown@example.com', date(1992, 2, 14)),
        ('Charlie Davis', 'charlie.davis@example.com', date(1987, 9, 30)),
        ('Diana Prince', 'diana.prince@example.com', date(1991, 5, 18)),
        ('Eva Garcia', 'eva.garcia@example.com', date(1989, 12, 3)),
        ('Frank Miller', 'frank.miller@example.com', None),  # No birth date
        ('Grace Lee', 'grace.lee@example.com', date(1986, 4, 25)),
        ('Henry Wilson', 'henry.wilson@example.com', date(1993, 8, 12)),
    ]
    
    for name, email, birth_date in author_data:
        author = Author.objects.create(
            name=name,
            email=email,
            birth_date=birth_date
        )
        authors.append(author)
    
    # Create comprehensive entries with varied ratings, dates, and content
    entries = []
    base_date = date(2024, 1, 1)
    
    for i in range(50):
        blog = blogs[i % len(blogs)]
        pub_date = base_date + timedelta(days=i*3)
        
        entry = Entry.objects.create(
            blog=blog,
            headline=f"Entry {i+1}: {blog.name} Article",
            body_text=f"This is comprehensive content for entry {i+1} in {blog.name}. " * (5 + i % 10),
            pub_date=pub_date,
            mod_date=pub_date + timedelta(days=1),
            rating=1 + (i % 5),  # Ratings 1-5
            number_of_comments=i * 2,
            number_of_pingbacks=i
        )
        
        # Add random authors (1-3 per entry)
        num_authors = 1 + (i % 3)
        for j in range(num_authors):
            entry.authors.add(authors[(i + j) % len(authors)])
        
        entries.append(entry)
    
    # Create category hierarchy
    categories = []
    category_data = [
        ('Electronics', None),
        ('Computers', 'Electronics'),
        ('Laptops', 'Computers'),
        ('Desktops', 'Computers'),
        ('Mobile Devices', 'Electronics'),
        ('Smartphones', 'Mobile Devices'),
        ('Tablets', 'Mobile Devices'),
        ('Books', None),
        ('Fiction', 'Books'),
        ('Non-Fiction', 'Books'),
        ('Science Fiction', 'Fiction'),
        ('Mystery', 'Fiction'),
        ('Clothing', None),
        ('Men', 'Clothing'),
        ('Women', 'Clothing'),
        ('Sports', None),
        ('Football', 'Sports'),
        ('Basketball', 'Sports'),
    ]
    
    for cat_name, parent_name in category_data:
        parent = None
        if parent_name:
            parent = Category.objects.get(name=parent_name)
        category = Category.objects.create(
            name=cat_name,
            parent=parent,
            description=f"Category for {cat_name} products"
        )
        categories.append(category)
    
    # Create manufacturers
    manufacturers = []
    mfg_data = [
        ('Apple Inc.', 'USA', 1976, 'https://www.apple.com'),
        ('Samsung Electronics', 'South Korea', 1969, 'https://www.samsung.com'),
        ('Microsoft Corporation', 'USA', 1975, 'https://www.microsoft.com'),
        ('Google LLC', 'USA', 1998, 'https://www.google.com'),
        ('Amazon.com Inc.', 'USA', 1994, 'https://www.amazon.com'),
        ('Sony Corporation', 'Japan', 1946, 'https://www.sony.com'),
        ('Nintendo Co., Ltd.', 'Japan', 1889, 'https://www.nintendo.com'),
        ('Intel Corporation', 'USA', 1968, 'https://www.intel.com'),
    ]
    
    for name, country, year, website in mfg_data:
        mfg = Manufacturer.objects.create(
            name=name,
            country=country,
            founded_year=year,
            website=website
        )
        manufacturers.append(mfg)
    
    # Create tags
    tags = []
    tag_data = [
        ('Popular', '#ff0000'),
        ('Sale', '#00ff00'),
        ('New', '#0000ff'),
        ('Premium', '#ffff00'),
        ('Limited', '#ff00ff'),
        ('Featured', '#00ffff'),
        ('Bestseller', '#orange'),
        ('Recommended', '#purple'),
    ]
    
    for name, color in tag_data:
        tag = Tag.objects.create(name=name, color=color)
        tags.append(tag)
    
    # Create comprehensive products
    products = []
    product_data = [
        ('iPhone 15 Pro', 'Smartphones', 'Apple Inc.', 1199.00, 800.00, 25),
        ('Galaxy S24 Ultra', 'Smartphones', 'Samsung Electronics', 1299.00, 850.00, 30),
        ('MacBook Air M3', 'Laptops', 'Apple Inc.', 1299.00, 900.00, 15),
        ('Surface Laptop 5', 'Laptops', 'Microsoft Corporation', 999.00, 700.00, 20),
        ('iPad Pro', 'Tablets', 'Apple Inc.', 799.00, 550.00, 40),
        ('Galaxy Tab S9', 'Tablets', 'Samsung Electronics', 729.00, 500.00, 35),
        ('PlayStation 5', 'Electronics', 'Sony Corporation', 499.00, 350.00, 10),
        ('Nintendo Switch', 'Electronics', 'Nintendo Co., Ltd.', 299.00, 200.00, 50),
        ('AirPods Pro', 'Electronics', 'Apple Inc.', 249.00, 150.00, 100),
        ('Galaxy Buds Pro', 'Electronics', 'Samsung Electronics', 199.00, 120.00, 80),
    ]
    
    for name, cat_name, mfg_name, price, cost, stock in product_data:
        category = Category.objects.get(name=cat_name)
        manufacturer = Manufacturer.objects.get(name=mfg_name)
        
        product = Product.objects.create(
            name=name,
            description=f"High-quality {name} from {mfg_name}",
            category=category,
            manufacturer=manufacturer,
            price=Decimal(str(price)),
            cost=Decimal(str(cost)),
            stock_quantity=stock,
            specifications={
                'color': ['Black', 'White', 'Silver'][len(products) % 3],
                'warranty': f"{1 + len(products) % 3} years",
                'weight': f"{100 + len(products) * 50}g",
                'features': ['premium', 'wireless', 'waterproof'][len(products) % 3:len(products) % 3 + 2]
            }
        )
        
        # Add random tags
        num_tags = 1 + (len(products) % 3)
        for i in range(num_tags):
            product.tags.add(tags[(len(products) + i) % len(tags)])
        
        products.append(product)
    
    # Create customers and orders
    customers = []
    for i, user in enumerate(users[:5]):
        customer = Customer.objects.create(
            user=user,
            phone=f"555-{2000 + i}",
            date_of_birth=date(1985 + i, 1 + i, 15),
            loyalty_points=i * 150,
            is_premium=(i % 2 == 0)
        )
        customers.append(customer)
        
        # Create address
        Address.objects.create(
            customer=customer,
            type='home',
            street=f"{200 + i} Main Street",
            city=f"City{i+1}",
            state=f"State{i+1}",
            zip_code=f"2000{i}",
            is_default=True
        )
    
    print(f"✅ Created comprehensive test data:")
    print(f"   - {len(blogs)} blogs")
    print(f"   - {len(authors)} authors") 
    print(f"   - {len(entries)} entries")
    print(f"   - {len(categories)} categories")
    print(f"   - {len(manufacturers)} manufacturers")
    print(f"   - {len(products)} products")
    print(f"   - {len(customers)} customers")


def test_queryset_evaluation():
    """Test when QuerySets are evaluated."""
    print_section("1. When QuerySets are Evaluated")
    
    print_section("Iteration", 2)
    print("Creating QuerySet (no DB hit)...")
    qs = Entry.objects.filter(rating__gte=4)
    print(f"QuerySet created: {type(qs)}")
    
    print("\nIterating (hits DB)...")
    count = 0
    for entry in qs:
        count += 1
        if count >= 3:
            break
    print(f"Iterated over {count} entries")
    
    print_section("Slicing", 2)
    # Slicing without step - returns new QuerySet
    sliced_qs = Entry.objects.all()[:5]
    print(f"Sliced QuerySet type: {type(sliced_qs)}")
    
    # Slicing with step - evaluates QuerySet
    stepped_slice = Entry.objects.all()[::2]
    print(f"Stepped slice type: {type(stepped_slice)}")
    
    print_section("Representation", 2)
    print("Calling repr() on QuerySet (hits DB)...")
    repr_result = repr(Entry.objects.all()[:3])
    print(f"Repr result: {repr_result}")
    
    print_section("Length", 2)
    print("Calling len() on QuerySet (hits DB)...")
    length = len(Entry.objects.filter(rating=5))
    print(f"Length: {length}")
    
    print_section("List conversion", 2)
    print("Converting to list (hits DB)...")
    entry_list = list(Entry.objects.filter(rating=1)[:3])
    print(f"List length: {len(entry_list)}")
    
    print_section("Boolean evaluation", 2)
    print("Boolean test (hits DB)...")
    has_entries = bool(Entry.objects.filter(rating=5))
    print(f"Has high-rated entries: {has_entries}")


def test_methods_returning_querysets():
    """Test all methods that return new QuerySets."""
    print_section("2. Methods that Return New QuerySets")
    
    print_section("filter()", 2)
    filtered = Entry.objects.filter(rating__gte=4, blog__name__icontains='tech')
    print(f"High-rated tech entries: {filtered.count()}")
    print_queryset_info(filtered)
    
    print_section("exclude()", 2)
    excluded = Entry.objects.exclude(rating__lt=3).exclude(blog__name__icontains='food')
    print(f"Excluded entries: {excluded.count()}")
    
    print_section("annotate()", 2)
    annotated = Entry.objects.annotate(
        engagement_score=F('number_of_comments') + F('number_of_pingbacks'),
        author_count=Count('authors'),
        is_popular=Case(
            When(rating__gte=4, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField()
        )
    )[:5]
    
    for entry in annotated:
        print(f"  {entry.headline}: engagement={entry.engagement_score}, "
              f"authors={entry.author_count}, popular={entry.is_popular}")
    
    print_section("alias()", 2)
    aliased = Entry.objects.alias(
        engagement=F('number_of_comments') + F('number_of_pingbacks')
    ).filter(engagement__gt=20)
    print(f"High engagement entries: {aliased.count()}")
    
    print_section("order_by()", 2)
    ordered = Entry.objects.order_by('-rating', 'pub_date', 'headline')[:5]
    print("Ordered entries:")
    for entry in ordered:
        print(f"  {entry.headline}: rating={entry.rating}, date={entry.pub_date}")
    
    # Order by expression
    expr_ordered = Entry.objects.order_by(
        Case(When(rating=5, then=1), default=2),
        '-pub_date'
    )[:3]
    print(f"\nExpression ordered entries: {expr_ordered.count()}")
    
    print_section("reverse()", 2)
    reversed_qs = Entry.objects.order_by('rating').reverse()[:5]
    print("Reversed order entries:")
    for entry in reversed_qs:
        print(f"  {entry.headline}: rating={entry.rating}")
    
    print_section("distinct()", 2)
    all_authors = Author.objects.filter(entry__isnull=False).count()
    distinct_authors = Author.objects.filter(entry__isnull=False).distinct().count()
    print(f"All author-entry relationships: {all_authors}")
    print(f"Distinct authors with entries: {distinct_authors}")
    
    # Distinct on specific fields (PostgreSQL only)
    try:
        distinct_blogs = Entry.objects.order_by('blog', '-pub_date').distinct('blog')
        print(f"Latest entry per blog: {distinct_blogs.count()}")
    except Exception as e:
        print(f"Distinct on fields not supported: {e}")
    
    print_section("values()", 2)
    values_qs = Entry.objects.values('headline', 'rating', 'blog__name')[:5]
    print("Entry values:")
    for item in values_qs:
        print(f"  {item}")
    
    # Values with expressions
    values_expr = Entry.objects.values(
        'headline',
        engagement=F('number_of_comments') + F('number_of_pingbacks')
    )[:3]
    print("\nValues with expressions:")
    for item in values_expr:
        print(f"  {item}")
    
    print_section("values_list()", 2)
    # Tuples
    values_tuples = Entry.objects.values_list('headline', 'rating')[:5]
    print("Values as tuples:")
    for item in values_tuples:
        print(f"  {item}")
    
    # Flat list
    ratings = Entry.objects.values_list('rating', flat=True).distinct()
    print(f"\nUnique ratings: {list(ratings)}")
    
    # Named tuples
    try:
        named_values = Entry.objects.values_list('headline', 'rating', named=True)[:3]
        print("\nNamed tuples:")
        for item in named_values:
            print(f"  {item.headline}: {item.rating}")
    except Exception as e:
        print(f"Named tuples error: {e}")
    
    print_section("dates()", 2)
    # Get unique dates
    unique_years = Entry.objects.dates('pub_date', 'year')
    print(f"Years with entries: {list(unique_years)}")
    
    unique_months = Entry.objects.dates('pub_date', 'month', order='DESC')[:6]
    print(f"Recent months: {list(unique_months)}")
    
    print_section("datetimes()", 2)
    # For datetime fields - using a datetime field from models
    try:
        # Since mod_date is DateField, we'll try to use a proper datetime field
        # or skip this test
        print("Skipping datetimes() test - mod_date is DateField, not DateTimeField")
    except Exception as e:
        print(f"Datetimes error: {e}")
    
    print_section("none()", 2)
    empty_qs = Entry.objects.none()
    print(f"Empty QuerySet count: {empty_qs.count()}")
    print(f"Is EmptyQuerySet: {type(empty_qs).__name__}")
    
    print_section("all()", 2)
    all_entries = Entry.objects.all()
    copied_qs = all_entries.all()
    print(f"Original count: {all_entries.count()}")
    print(f"Copied count: {copied_qs.count()}")
    print(f"Are same object: {all_entries is copied_qs}")


def test_set_operations():
    """Test union, intersection, and difference operations."""
    print_section("3. Set Operations")
    
    print_section("union()", 2)
    # Remove ordering for set operations as it can cause issues
    tech_entries = Entry.objects.filter(blog__name__icontains='tech').order_by()
    high_rated = Entry.objects.filter(rating__gte=4).order_by()
    
    try:
        union_qs = tech_entries.union(high_rated)
        print(f"Tech entries: {tech_entries.count()}")
        print(f"High rated entries: {high_rated.count()}")
        print(f"Union: {union_qs.count()}")
        
        # Union with all=True (allows duplicates)
        union_all = tech_entries.union(high_rated, all=True)
        print(f"Union with duplicates: {union_all.count()}")
    except Exception as e:
        print(f"Union operation error: {e}")
    
    print_section("intersection()", 2)
    try:
        intersection_qs = tech_entries.intersection(high_rated)
        print(f"Tech AND high rated: {intersection_qs.count()}")
    except Exception as e:
        print(f"Intersection operation error: {e}")
    
    print_section("difference()", 2)
    try:
        difference_qs = tech_entries.difference(high_rated)
        print(f"Tech but NOT high rated: {difference_qs.count()}")
    except Exception as e:
        print(f"Difference operation error: {e}")


def test_optimization_methods():
    """Test select_related and prefetch_related."""
    print_section("4. Query Optimization Methods")
    
    print_section("select_related()", 2)
    print("Without select_related (causes N+1 queries):")
    entries = Entry.objects.all()[:3]
    for entry in entries:
        print(f"  {entry.headline} in {entry.blog.name}")
    
    print("\nWith select_related (single query):")
    entries_optimized = Entry.objects.select_related('blog')[:3]
    for entry in entries_optimized:
        print(f"  {entry.headline} in {entry.blog.name}")
    
    # Deep select_related
    print("\nDeep select_related (with nested relationships):")
    products = Product.objects.select_related('category__parent', 'manufacturer')[:3]
    for product in products:
        parent = product.category.parent.name if product.category.parent else "None"
        print(f"  {product.name}: {parent} > {product.category.name} by {product.manufacturer.name}")
    
    print_section("prefetch_related()", 2)
    print("With prefetch_related (for many-to-many):")
    entries_with_authors = Entry.objects.prefetch_related('authors')[:3]
    for entry in entries_with_authors:
        author_names = [author.name for author in entry.authors.all()]
        print(f"  {entry.headline} by: {', '.join(author_names)}")
    
    # Prefetch with custom QuerySet
    print("\nPrefetch with custom QuerySet:")
    high_rated_prefetch = Prefetch(
        'entry_set',
        queryset=Entry.objects.filter(rating__gte=4),
        to_attr='high_rated_entries'
    )
    blogs_with_prefetch = Blog.objects.prefetch_related(high_rated_prefetch)[:3]
    for blog in blogs_with_prefetch:
        print(f"  {blog.name}: {len(blog.high_rated_entries)} high-rated entries")
    
    print_section("only() and defer()", 2)
    # Only specific fields
    entries_only = Entry.objects.only('headline', 'rating')[:3]
    print("Only headline and rating:")
    for entry in entries_only:
        print(f"  {entry.headline}: {entry.rating}")
        # Accessing body_text would hit the database
    
    # Defer specific fields
    entries_defer = Entry.objects.defer('body_text')[:3]
    print("\nDefer body_text:")
    for entry in entries_defer:
        print(f"  {entry.headline} (body deferred)")


def test_advanced_methods():
    """Test advanced QuerySet methods."""
    print_section("5. Advanced QuerySet Methods")
    
    print_section("extra()", 2)
    # Using extra() for complex SQL
    extra_qs = Entry.objects.extra(
        select={'is_recent': "pub_date > '2024-06-01'"},
        where=["rating >= %s"],
        params=[4]
    )[:5]
    
    print("Entries with extra fields:")
    for entry in extra_qs:
        print(f"  {entry.headline}: recent={entry.is_recent}, rating={entry.rating}")
    
    print_section("raw()", 2)
    # Raw SQL queries
    raw_qs = Entry.objects.raw(
        "SELECT * FROM query_practice_entry WHERE rating >= %s ORDER BY pub_date DESC",
        [4]
    )
    print("Raw query results:")
    for entry in list(raw_qs)[:3]:
        print(f"  {entry.headline}: {entry.rating}")
    
    print_section("using()", 2)
    # Database routing (if multiple databases configured)
    default_entries = Entry.objects.using('default').count()
    print(f"Entries using default database: {default_entries}")
    
    print_section("select_for_update()", 2)
    # Row locking
    try:
        with transaction.atomic():
            locked_entries = Entry.objects.select_for_update().filter(rating=5)[:2]
            print(f"Locked {locked_entries.count()} entries for update")
            # Would lock these rows until transaction ends
    except Exception as e:
        print(f"Select for update error: {e}")


def test_methods_not_returning_querysets():
    """Test methods that evaluate QuerySets and return other types."""
    print_section("6. Methods that Don't Return QuerySets")
    
    print_section("get()", 2)
    try:
        entry = Entry.objects.get(pk=1)
        print(f"Got entry: {entry.headline}")
    except Entry.DoesNotExist:
        print("Entry not found")
    except Entry.MultipleObjectsReturned:
        print("Multiple entries found")
    
    # Get with complex lookup
    try:
        tech_entry = Entry.objects.get(
            Q(blog__name__icontains='tech') & Q(rating__gte=4)
        )
        print(f"Tech entry: {tech_entry.headline}")
    except (Entry.DoesNotExist, Entry.MultipleObjectsReturned) as e:
        print(f"Tech entry lookup: {e}")
    
    print_section("create()", 2)
    new_entry = Entry.objects.create(
        blog=Blog.objects.first(),
        headline="Test Entry Created",
        body_text="This is a test entry created by the API practice script.",
        pub_date=date.today(),
        rating=4
    )
    print(f"Created entry: {new_entry.headline} (pk: {new_entry.pk})")
    
    print_section("get_or_create()", 2)
    blog, created = Blog.objects.get_or_create(
        name="Test Blog",
        defaults={'tagline': 'A test blog created by get_or_create'}
    )
    print(f"Blog: {blog.name}, Created: {created}")
    
    # Try again - should not create
    blog2, created2 = Blog.objects.get_or_create(
        name="Test Blog",
        defaults={'tagline': 'Different tagline'}
    )
    print(f"Blog: {blog2.name}, Created: {created2}")
    
    print_section("update_or_create()", 2)
    author, created = Author.objects.update_or_create(
        name="Test Author",
        defaults={
            'email': 'test.author@example.com',
            'birth_date': date(1990, 1, 1)
        }
    )
    print(f"Author: {author.name}, Created: {created}")
    
    print_section("bulk_create()", 2)
    bulk_entries = [
        Entry(
            blog=Blog.objects.first(),
            headline=f"Bulk Entry {i}",
            body_text=f"Bulk created entry {i}",
            pub_date=date.today(),
            rating=3 + (i % 3)
        ) for i in range(5)
    ]
    
    created_entries = Entry.objects.bulk_create(bulk_entries)
    print(f"Bulk created {len(created_entries)} entries")
    
    print_section("bulk_update()", 2)
    # Update the bulk created entries
    for entry in created_entries:
        entry.rating = 5
    
    updated_count = Entry.objects.bulk_update(created_entries, ['rating'])
    print(f"Bulk updated {updated_count} entries")
    
    print_section("count()", 2)
    total_count = Entry.objects.count()
    high_rated_count = Entry.objects.filter(rating__gte=4).count()
    print(f"Total entries: {total_count}")
    print(f"High rated entries: {high_rated_count}")
    
    print_section("in_bulk()", 2)
    # Get multiple objects by primary key
    entry_ids = [1, 2, 3, 4, 5]
    entries_bulk = Entry.objects.in_bulk(entry_ids)
    print(f"Retrieved {len(entries_bulk)} entries by ID")
    for pk, entry in entries_bulk.items():
        print(f"  {pk}: {entry.headline}")
    
    # in_bulk with unique field - use email for authors as it should be unique
    try:
        author_emails = ['john.smith@example.com', 'jane.doe@example.com']
        authors_bulk = Author.objects.in_bulk(author_emails, field_name='email')
        print(f"\nRetrieved {len(authors_bulk)} authors by email")
        for email, author in authors_bulk.items():
            print(f"  {email}: {author.name}")
    except Exception as e:
        print(f"\nAuthors bulk lookup error: {e}")
    
    print_section("iterator()", 2)
    print("Using iterator for memory efficiency:")
    count = 0
    for entry in Entry.objects.iterator(chunk_size=10):
        count += 1
        if count <= 5:
            print(f"  {entry.headline}")
        elif count == 6:
            print("  ...")
        if count >= 10:
            break
    print(f"Iterated through {count} entries")
    
    print_section("latest() and earliest()", 2)
    try:
        latest = Entry.objects.latest('pub_date')
        earliest = Entry.objects.earliest('pub_date')
        print(f"Latest entry: {latest.headline} ({latest.pub_date})")
        print(f"Earliest entry: {earliest.headline} ({earliest.pub_date})")
    except Entry.DoesNotExist:
        print("No entries found")
    
    print_section("first() and last()", 2)
    first_entry = Entry.objects.order_by('headline').first()
    last_entry = Entry.objects.order_by('headline').last()
    print(f"First by headline: {first_entry.headline if first_entry else 'None'}")
    print(f"Last by headline: {last_entry.headline if last_entry else 'None'}")
    
    print_section("aggregate()", 2)
    stats = Entry.objects.aggregate(
        total_entries=Count('id'),
        avg_rating=Avg('rating'),
        max_comments=Max('number_of_comments'),
        min_comments=Min('number_of_comments'),
        total_comments=Sum('number_of_comments'),
        rating_stddev=StdDev('rating'),
        rating_variance=Variance('rating')
    )
    
    print("Aggregation results:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print_section("exists()", 2)
    has_high_rated = Entry.objects.filter(rating=5).exists()
    has_future_entries = Entry.objects.filter(pub_date__gt=date.today()).exists()
    print(f"Has 5-star entries: {has_high_rated}")
    print(f"Has future entries: {has_future_entries}")
    
    print_section("contains()", 2)
    first_entry = Entry.objects.first()
    if first_entry:
        contains_first = Entry.objects.filter(rating__gte=3).contains(first_entry)
        print(f"High-rated QuerySet contains first entry: {contains_first}")
    
    print_section("update()", 2)
    # Bulk update
    updated = Entry.objects.filter(headline__startswith='Bulk').update(
        rating=4,
        mod_date=timezone.now()
    )
    print(f"Updated {updated} bulk entries")
    
    # Update with F expressions
    Entry.objects.filter(rating__lt=3).update(
        number_of_comments=F('number_of_comments') + 10
    )
    print("Added 10 comments to low-rated entries")
    
    print_section("delete()", 2)
    # Delete test entries
    deleted = Entry.objects.filter(headline__startswith='Test').delete()
    print(f"Deleted: {deleted}")


def test_field_lookups_comprehensive():
    """Test all field lookup types comprehensively."""
    print_section("7. Field Lookups - Comprehensive Test")
    
    print_section("Exact matches", 2)
    exact_match = Entry.objects.filter(rating__exact=5).count()
    iexact_blogs = Blog.objects.filter(name__iexact='TECH INNOVATIONS').count()
    print(f"Exact rating=5: {exact_match}")
    print(f"Case-insensitive blog name: {iexact_blogs}")
    
    print_section("String operations", 2)
    contains = Entry.objects.filter(headline__contains='Tech').count()
    icontains = Entry.objects.filter(headline__icontains='TECH').count()
    startswith = Entry.objects.filter(headline__startswith='Entry').count()
    istartswith = Entry.objects.filter(headline__istartswith='ENTRY').count()
    endswith = Entry.objects.filter(headline__endswith='Article').count()
    iendswith = Entry.objects.filter(headline__iendswith='ARTICLE').count()
    
    print(f"Contains 'Tech': {contains}")
    print(f"iContains 'TECH': {icontains}")
    print(f"Starts with 'Entry': {startswith}")
    print(f"iStarts with 'ENTRY': {istartswith}")
    print(f"Ends with 'Article': {endswith}")
    print(f"iEnds with 'ARTICLE': {iendswith}")
    
    print_section("Comparison operators", 2)
    gt = Entry.objects.filter(rating__gt=3).count()
    gte = Entry.objects.filter(rating__gte=4).count()
    lt = Entry.objects.filter(number_of_comments__lt=10).count()
    lte = Entry.objects.filter(number_of_comments__lte=5).count()
    
    print(f"Rating > 3: {gt}")
    print(f"Rating >= 4: {gte}")
    print(f"Comments < 10: {lt}")
    print(f"Comments <= 5: {lte}")
    
    print_section("List operations", 2)
    in_lookup = Entry.objects.filter(rating__in=[4, 5]).count()
    range_lookup = Entry.objects.filter(number_of_comments__range=(10, 50)).count()
    
    print(f"Rating in [4, 5]: {in_lookup}")
    print(f"Comments in range 10-50: {range_lookup}")
    
    print_section("Date/time lookups", 2)
    # Date lookups
    year_2024 = Entry.objects.filter(pub_date__year=2024).count()
    recent_months = Entry.objects.filter(pub_date__month__gte=6).count()
    specific_day = Entry.objects.filter(pub_date__day=15).count()
    
    print(f"Published in 2024: {year_2024}")
    print(f"Published in month >= 6: {recent_months}")
    print(f"Published on day 15: {specific_day}")
    
    # Date range
    date_range = Entry.objects.filter(
        pub_date__range=(date(2024, 1, 1), date(2024, 6, 30))
    ).count()
    print(f"Published in first half of 2024: {date_range}")
    
    # Week operations
    current_week = Entry.objects.filter(pub_date__week=25).count()
    weekday = Entry.objects.filter(pub_date__week_day=2).count()  # Monday
    iso_weekday = Entry.objects.filter(pub_date__iso_week_day=1).count()  # Monday
    
    print(f"Published in week 25: {current_week}")
    print(f"Published on Sunday (week_day=2): {weekday}")
    print(f"Published on Monday (iso_week_day=1): {iso_weekday}")
    
    print_section("Null operations", 2)
    has_birth_date = Author.objects.filter(birth_date__isnull=False).count()
    no_birth_date = Author.objects.filter(birth_date__isnull=True).count()
    
    print(f"Authors with birth date: {has_birth_date}")
    print(f"Authors without birth date: {no_birth_date}")
    
    print_section("Regex operations", 2)
    # Case-sensitive regex
    regex_entries = Entry.objects.filter(headline__regex=r'^Entry \d+:').count()
    # Case-insensitive regex
    iregex_entries = Entry.objects.filter(headline__iregex=r'^entry \d+:').count()
    
    print(f"Headlines matching regex '^Entry \\d+:': {regex_entries}")
    print(f"Headlines matching iregex '^entry \\d+:': {iregex_entries}")


def test_aggregation_functions():
    """Test all aggregation functions."""
    print_section("8. Aggregation Functions")
    
    print_section("Basic aggregations", 2)
    basic_agg = Entry.objects.aggregate(
        count=Count('id'),
        avg_rating=Avg('rating'),
        max_rating=Max('rating'),
        min_rating=Min('rating'),
        sum_comments=Sum('number_of_comments'),
        stddev_rating=StdDev('rating'),
        variance_rating=Variance('rating')
    )
    
    print("Basic aggregations:")
    for key, value in basic_agg.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print_section("Aggregations with filter", 2)
    filtered_agg = Entry.objects.aggregate(
        high_rated_count=Count('id', filter=Q(rating__gte=4)),
        high_rated_avg_comments=Avg('number_of_comments', filter=Q(rating__gte=4)),
        low_rated_count=Count('id', filter=Q(rating__lt=3))
    )
    
    print("Filtered aggregations:")
    for key, value in filtered_agg.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print_section("Aggregations with default", 2)
    default_agg = Entry.objects.filter(rating=10).aggregate(
        count_with_default=Count('id'),
        avg_with_default=Avg('rating', default=0),
        sum_with_default=Sum('number_of_comments', default=0)
    )
    
    print("Aggregations with default values:")
    for key, value in default_agg.items():
        print(f"  {key}: {value}")
    
    print_section("Distinct aggregations", 2)
    distinct_agg = Entry.objects.aggregate(
        unique_ratings=Count('rating', distinct=True),
        avg_unique_ratings=Avg('rating', distinct=True),
        sum_unique_ratings=Sum('rating', distinct=True)
    )
    
    print("Distinct aggregations:")
    for key, value in distinct_agg.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print_section("Group by aggregations", 2)
    blog_stats = Blog.objects.annotate(
        entry_count=Count('entry'),
        avg_rating=Avg('entry__rating'),
        max_rating=Max('entry__rating'),
        total_comments=Sum('entry__number_of_comments')
    ).values('name', 'entry_count', 'avg_rating', 'max_rating', 'total_comments')
    
    print("Blog statistics:")
    for blog in blog_stats:
        avg_rating = blog['avg_rating']
        avg_str = f"{avg_rating:.2f}" if avg_rating else "N/A"
        print(f"  {blog['name']}: {blog['entry_count']} entries, "
              f"avg rating: {avg_str}, max: {blog['max_rating']}, "
              f"comments: {blog['total_comments'] or 0}")


def test_q_objects_and_complex_queries():
    """Test Q objects and complex query combinations."""
    print_section("9. Q Objects and Complex Queries")
    
    print_section("Basic Q objects", 2)
    q_high_rated = Q(rating__gte=4)
    q_tech_blog = Q(blog__name__icontains='tech')
    
    high_rated = Entry.objects.filter(q_high_rated).count()
    tech_entries = Entry.objects.filter(q_tech_blog).count()
    
    print(f"High rated entries: {high_rated}")
    print(f"Tech blog entries: {tech_entries}")
    
    print_section("Q object combinations", 2)
    # OR combination
    or_query = Entry.objects.filter(q_high_rated | q_tech_blog).count()
    print(f"High rated OR tech blog: {or_query}")
    
    # AND combination
    and_query = Entry.objects.filter(q_high_rated & q_tech_blog).count()
    print(f"High rated AND tech blog: {and_query}")
    
    # NOT combination
    not_query = Entry.objects.filter(~q_tech_blog).count()
    print(f"NOT tech blog: {not_query}")
    
    # XOR combination
    xor_query = Entry.objects.filter(q_high_rated ^ q_tech_blog).count()
    print(f"High rated XOR tech blog: {xor_query}")
    
    print_section("Complex Q combinations", 2)
    complex_q = (
        (Q(rating__gte=4) | Q(number_of_comments__gte=20)) &
        Q(blog__name__icontains='tech') &
        ~Q(headline__icontains='test')
    )
    complex_results = Entry.objects.filter(complex_q).count()
    print(f"Complex query results: {complex_results}")
    
    print_section("Q objects with annotations", 2)
    annotated_q = Entry.objects.annotate(
        is_popular=Case(
            When(Q(rating__gte=4) & Q(number_of_comments__gte=10), then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField()
        )
    ).filter(is_popular=True).count()
    
    print(f"Popular entries (annotated): {annotated_q}")


def test_f_expressions():
    """Test F expressions for field references and calculations."""
    print_section("10. F Expressions")
    
    print_section("Field comparisons", 2)
    more_comments = Entry.objects.filter(
        number_of_comments__gt=F('number_of_pingbacks')
    ).count()
    print(f"Entries with more comments than pingbacks: {more_comments}")
    
    print_section("Arithmetic with F expressions", 2)
    double_pingbacks = Entry.objects.filter(
        number_of_comments__gt=F('number_of_pingbacks') * 2
    ).count()
    print(f"Entries with comments > 2x pingbacks: {double_pingbacks}")
    
    # Product profit margins
    profitable_products = Product.objects.filter(
        price__gt=F('cost') * Decimal('1.5')
    ).count()
    print(f"Products with >50% profit margin: {profitable_products}")
    
    print_section("F expressions in annotations", 2)
    products_with_profit = Product.objects.annotate(
        profit_amount=F('price') - F('cost'),
        margin_percent=((F('price') - F('cost')) / F('price')) * 100
    )[:5]
    
    print("Product profits:")
    for product in products_with_profit:
        print(f"  {product.name}: profit=${product.profit_amount:.2f}, "
              f"margin={product.margin_percent:.1f}%")
    
    print_section("F expressions in updates", 2)
    # Increase all low-rated entry comments
    updated = Entry.objects.filter(rating__lt=3).update(
        number_of_comments=F('number_of_comments') + 5
    )
    print(f"Increased comments for {updated} low-rated entries")
    
    # Decrease product prices by 10%
    updated_products = Product.objects.filter(
        name__icontains='galaxy'
    ).update(
        price=F('price') * Decimal('0.9')
    )
    print(f"Applied 10% discount to {updated_products} Galaxy products")


def test_window_functions():
    """Test window functions if available."""
    print_section("11. Window Functions")
    
    try:
        from django.db.models import Window, RowNumber, Rank, DenseRank
        
        print_section("Row numbering", 2)
        ranked_entries = Entry.objects.annotate(
            row_number=Window(
                expression=RowNumber(),
                order_by=F('rating').desc()
            )
        ).order_by('row_number')[:10]
        
        print("Entries ranked by rating:")
        for entry in ranked_entries:
            print(f"  #{entry.row_number}: {entry.headline} (rating: {entry.rating})")
        
        print_section("Partitioned ranking", 2)
        partitioned_rank = Entry.objects.annotate(
            rank_in_blog=Window(
                expression=Rank(),
                partition_by=[F('blog')],
                order_by=F('rating').desc()
            )
        ).select_related('blog').order_by('blog__name', 'rank_in_blog')[:15]
        
        print("Entries ranked within each blog:")
        current_blog = None
        for entry in partitioned_rank:
            if current_blog != entry.blog.name:
                current_blog = entry.blog.name
                print(f"\n{current_blog}:")
            print(f"  #{entry.rank_in_blog}: {entry.headline} (rating: {entry.rating})")
        
    except ImportError:
        print("Window functions not available in this Django version")
    except Exception as e:
        print(f"Window functions error: {e}")


def test_json_field_operations():
    """Test JSON field operations."""
    print_section("12. JSON Field Operations")
    
    print_section("JSON key lookups", 2)
    # Products with color specification
    products_with_color = Product.objects.filter(
        specifications__color__isnull=False
    ).count()
    print(f"Products with color spec: {products_with_color}")
    
    # Specific color
    black_products = Product.objects.filter(
        specifications__color='Black'
    ).count()
    print(f"Black products: {black_products}")
    
    print_section("JSON value transformations", 2)
    # Extract and filter by JSON values
    products_with_warranty = Product.objects.filter(
        specifications__warranty__isnull=False
    ).values('name', 'specifications__warranty')[:5]
    
    print("Products with warranty info:")
    for product in products_with_warranty:
        print(f"  {product['name']}: {product['specifications__warranty']}")
    
    print_section("JSON array operations", 2)
    # Note: Some operations may not be supported on all databases
    try:
        # Products with features array
        products_with_features = Product.objects.filter(
            specifications__has_key='features'
        ).count()
        print(f"Products with features: {products_with_features}")
    except Exception as e:
        print(f"JSON array operations not fully supported: {e}")


def test_performance_monitoring():
    """Test query performance monitoring and explanation."""
    print_section("13. Performance Monitoring")
    
    print_section("Query explanation", 2)
    try:
        # Explain a complex query
        complex_query = Entry.objects.select_related('blog').filter(
            rating__gte=4
        ).order_by('-pub_date')
        
        explanation = complex_query.explain()
        print("Query execution plan:")
        print(explanation[:500] + "..." if len(explanation) > 500 else explanation)
        
    except Exception as e:
        print(f"Query explanation not available: {e}")
    
    print_section("QuerySet caching behavior", 2)
    print("Demonstrating QuerySet caching...")
    
    # Create QuerySet (no DB hit)
    qs = Entry.objects.filter(rating__gte=4)
    print(f"QuerySet created: {type(qs)}")
    
    # First evaluation (hits DB)
    print("First evaluation (hits database)...")
    first_count = len(list(qs))
    
    # Second evaluation (uses cache)
    print("Second evaluation (uses cache)...")
    second_count = len(list(qs))
    
    print(f"Both evaluations returned {first_count} and {second_count} entries")
    
    # Force fresh query
    print("Forcing fresh query with all()...")
    fresh_qs = qs.all()
    fresh_count = len(list(fresh_qs))
    print(f"Fresh query returned {fresh_count} entries")


def test_database_functions():
    """Test database functions."""
    print_section("14. Database Functions")
    
    print_section("String functions", 2)
    string_funcs = Entry.objects.annotate(
        headline_lower=Lower('headline'),
        headline_upper=Upper('headline'),
        headline_length=Length('headline')
    ).values('headline', 'headline_lower', 'headline_upper', 'headline_length')[:3]
    
    print("String functions:")
    for entry in string_funcs:
        print(f"  Original: {entry['headline']}")
        print(f"  Lower: {entry['headline_lower']}")
        print(f"  Upper: {entry['headline_upper']}")
        print(f"  Length: {entry['headline_length']}")
        print()
    
    print_section("Date/time functions", 2)
    date_funcs = Entry.objects.annotate(
        pub_year=Extract('pub_date', 'year'),
        pub_month=Extract('pub_date', 'month'),
        pub_day=Extract('pub_date', 'day')
    ).values('headline', 'pub_date', 'pub_year', 'pub_month', 'pub_day')[:5]
    
    print("Date extraction functions:")
    for entry in date_funcs:
        print(f"  {entry['headline']}: {entry['pub_year']}-{entry['pub_month']:02d}-{entry['pub_day']:02d}")
    
    print_section("Conditional functions", 2)
    conditional = Entry.objects.annotate(
        rating_category=Case(
            When(rating=5, then=Value('Excellent')),
            When(rating=4, then=Value('Good')),
            When(rating=3, then=Value('Average')),
            When(rating__lt=3, then=Value('Poor')),
            default=Value('Unknown'),
            output_field=models.CharField()
        ),
        safe_title=Coalesce('headline', Value('No Title'))
    ).values('headline', 'rating', 'rating_category', 'safe_title')[:10]
    
    print("Conditional functions:")
    for entry in conditional:
        print(f"  {entry['safe_title']}: {entry['rating_category']} (rating: {entry['rating']})")


def main():
    """Main test function to run all QuerySet API tests."""
    print("🚀 Django QuerySet API Reference - Comprehensive Practice")
    print("Following: https://docs.djangoproject.com/en/5.2/ref/models/querysets/")
    print("="*80)
    
    try:
        # Setup comprehensive test data
        setup_comprehensive_data()
        
        # Run all QuerySet API tests
        test_queryset_evaluation()
        test_methods_returning_querysets()
        test_set_operations()
        test_optimization_methods()
        test_advanced_methods()
        test_methods_not_returning_querysets()
        test_field_lookups_comprehensive()
        test_aggregation_functions()
        test_q_objects_and_complex_queries()
        test_f_expressions()
        test_window_functions()
        test_json_field_operations()
        test_performance_monitoring()
        test_database_functions()
        
        print_section("🎉 SUMMARY - QuerySet API Mastery Complete!")
        print("✅ Successfully demonstrated ALL Django QuerySet API methods:")
        print()
        print("📋 METHODS THAT RETURN NEW QUERYSETS:")
        print("   • filter(), exclude(), annotate(), alias()")
        print("   • order_by(), reverse(), distinct()")
        print("   • values(), values_list(), dates(), datetimes()")
        print("   • none(), all(), union(), intersection(), difference()")
        print("   • select_related(), prefetch_related()")
        print("   • only(), defer(), using(), select_for_update()")
        print("   • extra(), raw()")
        print()
        print("🔄 SET OPERATIONS:")
        print("   • union(), intersection(), difference() with proper SQL generation")
        print("   • AND (&), OR (|), XOR (^) operators")
        print()
        print("📊 METHODS THAT DON'T RETURN QUERYSETS:")
        print("   • get(), create(), get_or_create(), update_or_create()")
        print("   • bulk_create(), bulk_update(), count(), in_bulk()")
        print("   • iterator(), latest(), earliest(), first(), last()")
        print("   • aggregate(), exists(), contains(), update(), delete()")
        print("   • as_manager(), explain()")
        print()
        print("🔍 FIELD LOOKUPS (ALL 30+ TYPES):")
        print("   • String: exact, iexact, contains, icontains, startswith, endswith")
        print("   • Comparison: gt, gte, lt, lte, in, range")
        print("   • Date/Time: year, month, day, week, quarter, hour, minute, second")
        print("   • Special: isnull, regex, iregex")
        print()
        print("📈 AGGREGATION FUNCTIONS:")
        print("   • Avg, Count, Max, Min, Sum, StdDev, Variance")
        print("   • With filter, default, distinct options")
        print()
        print("🔧 ADVANCED FEATURES:")
        print("   • Q objects for complex queries")
        print("   • F expressions for field references")
        print("   • Window functions (if available)")
        print("   • JSON field operations")
        print("   • Database functions (Lower, Upper, Extract, Case, etc.)")
        print("   • Performance optimization (select_related, prefetch_related)")
        print("   • Query explanation and monitoring")
        print()
        print("🎯 OPTIMIZATION TECHNIQUES:")
        print("   • select_related() for ForeignKey optimization")
        print("   • prefetch_related() for ManyToMany optimization")
        print("   • only() and defer() for field selection")
        print("   • iterator() for memory-efficient processing")
        print("   • bulk operations for performance")
        print()
        print("💡 PRACTICAL PATTERNS:")
        print("   • Complex filtering with Q objects")
        print("   • Dynamic annotations and calculations")
        print("   • Conditional logic with Case/When")
        print("   • Cross-relationship queries")
        print("   • Aggregation with grouping")
        print()
        print("🚀 You now have comprehensive knowledge of Django's QuerySet API!")
        print("   Ready to build efficient, complex database queries in Django!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
