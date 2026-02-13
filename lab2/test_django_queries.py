#!/usr/bin/env python
"""
Django Database Queries Practice Script
Following https://docs.djangoproject.com/en/5.2/topics/db/queries/

This script demonstrates all important Django database query concepts.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.db import models
from django.db.models import Q, F, Count, Sum, Avg, Max, Min, Case, When, Value
from django.db.models.functions import Lower, Upper, Concat, Extract
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modelspractice.settings')
    django.setup()

from django.contrib.auth.models import User
from query_practice.models import (
    Blog, Author, Entry, EntryDetail, Category, Manufacturer, Product, Tag,
    Customer, Address, Order, OrderItem, Review, ProductView, SalesMetrics,
    Warehouse, Inventory, Promotion, WishList, WishListItem, ProductBundle, BundleItem
)


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}")


def setup_sample_data():
    """Create sample data for testing queries."""
    print_section("Setting up Sample Data")
    
    # Clear existing data (order matters due to foreign keys)
    Entry.objects.all().delete()
    Blog.objects.all().delete()
    Author.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    Manufacturer.objects.all().delete()
    Tag.objects.all().delete()
    Customer.objects.all().delete()
    User.objects.filter(username__startswith='test').delete()
    
    print("Cleared existing data...")
    
    # Create users
    users = []
    for i in range(5):
        user = User.objects.create_user(
            username=f'testuser{i+1}',
            email=f'test{i+1}@example.com',
            first_name=f'User{i+1}',
            last_name='Test'
        )
        users.append(user)
    
    # Create blogs
    blogs = []
    blog_names = ['Tech Blog', 'Food Blog', 'Travel Blog', 'Fashion Blog', 'Music Blog']
    for i, name in enumerate(blog_names):
        blog = Blog.objects.create(
            name=name,
            tagline=f"All about {name.split()[0].lower()}"
        )
        blogs.append(blog)
    
    # Create authors
    authors = []
    author_names = ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson']
    for i, name in enumerate(author_names):
        author = Author.objects.create(
            name=name,
            email=f'{name.lower().replace(" ", ".")}@example.com',
            birth_date=date(1980 + i, 1 + i, 10 + i)
        )
        authors.append(author)
    
    # Create entries
    entries = []
    for i in range(15):
        blog = blogs[i % len(blogs)]
        entry = Entry.objects.create(
            blog=blog,
            headline=f"Article {i+1}: {blog.name} Content",
            body_text=f"This is the body text for article {i+1} in {blog.name}. " * 5,
            pub_date=date.today() - timedelta(days=i*2),
            rating=3 + (i % 3),
            number_of_comments=i * 2,
            number_of_pingbacks=i
        )
        # Add random authors
        entry.authors.add(authors[i % len(authors)])
        if i % 3 == 0:  # Some entries have multiple authors
            entry.authors.add(authors[(i+1) % len(authors)])
        entries.append(entry)
    
    # Create categories
    categories = []
    cat_data = [
        ('Electronics', None),
        ('Smartphones', 'Electronics'),
        ('Laptops', 'Electronics'),
        ('Clothing', None),
        ('Men Clothing', 'Clothing'),
        ('Women Clothing', 'Clothing'),
        ('Books', None),
        ('Fiction', 'Books'),
        ('Non-Fiction', 'Books'),
    ]
    
    for cat_name, parent_name in cat_data:
        parent = None
        if parent_name:
            parent = Category.objects.get(name=parent_name)
        category = Category.objects.create(
            name=cat_name,
            parent=parent,
            description=f"Category for {cat_name}"
        )
        categories.append(category)
    
    # Create manufacturers
    manufacturers = []
    mfg_data = [
        ('Apple', 'USA', 1976),
        ('Samsung', 'South Korea', 1938),
        ('Sony', 'Japan', 1946),
        ('Nike', 'USA', 1964),
        ('Adidas', 'Germany', 1949),
    ]
    
    for name, country, year in mfg_data:
        mfg = Manufacturer.objects.create(
            name=name,
            country=country,
            founded_year=year,
            website=f"https://www.{name.lower()}.com"
        )
        manufacturers.append(mfg)
    
    # Create tags
    tags = []
    tag_names = ['Popular', 'Sale', 'New', 'Premium', 'Trending']
    colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff']
    
    for name, color in zip(tag_names, colors):
        tag = Tag.objects.create(name=name, color=color)
        tags.append(tag)
    
    # Create products
    products = []
    product_data = [
        ('iPhone 15', 'Electronics/Smartphones', 'Apple', 999.00, 700.00),
        ('Galaxy S24', 'Electronics/Smartphones', 'Samsung', 899.00, 650.00),
        ('MacBook Pro', 'Electronics/Laptops', 'Apple', 1999.00, 1400.00),
        ('Air Jordan 1', 'Clothing/Men Clothing', 'Nike', 150.00, 80.00),
        ('Ultraboost 22', 'Clothing/Men Clothing', 'Adidas', 180.00, 100.00),
        ('WH-1000XM5', 'Electronics', 'Sony', 399.00, 250.00),
    ]
    
    for name, cat_path, mfg_name, price, cost in product_data:
        # Get category
        if '/' in cat_path:
            cat_name = cat_path.split('/')[-1]
        else:
            cat_name = cat_path
        category = Category.objects.get(name=cat_name)
        manufacturer = Manufacturer.objects.get(name=mfg_name)
        
        product = Product.objects.create(
            name=name,
            description=f"High-quality {name} from {mfg_name}",
            category=category,
            manufacturer=manufacturer,
            price=Decimal(str(price)),
            cost=Decimal(str(cost)),
            stock_quantity=50 + (len(products) * 10),
            specifications={
                'color': ['Black', 'White'][len(products) % 2],
                'warranty': '1 year',
                'weight': f"{len(products) + 1}00g"
            }
        )
        # Add random tags
        product.tags.add(tags[len(products) % len(tags)])
        if len(products) % 2 == 0:
            product.tags.add(tags[(len(products) + 1) % len(tags)])
        
        products.append(product)
    
    # Create customers
    customers = []
    for i, user in enumerate(users):
        customer = Customer.objects.create(
            user=user,
            phone=f"555-{1000 + i}",
            date_of_birth=date(1990 + i, 1 + i, 15),
            loyalty_points=i * 100,
            is_premium=(i % 2 == 0)
        )
        customers.append(customer)
        
        # Create addresses for each customer
        Address.objects.create(
            customer=customer,
            type='home',
            street=f"{100 + i} Main St",
            city=f"City{i+1}",
            state=f"State{i+1}",
            zip_code=f"1000{i}",
            is_default=True
        )
    
    print(f"✅ Created sample data:")
    print(f"   - {len(blogs)} blogs")
    print(f"   - {len(authors)} authors") 
    print(f"   - {len(entries)} entries")
    print(f"   - {len(categories)} categories")
    print(f"   - {len(manufacturers)} manufacturers")
    print(f"   - {len(products)} products")
    print(f"   - {len(customers)} customers")


def test_creating_objects():
    """Test creating objects in different ways."""
    print_section("1. Creating Objects")
    
    # Method 1: Create and save manually
    print("\n--- Method 1: Create and save manually ---")
    blog = Blog(name="Manual Blog", tagline="Created manually")
    print(f"Before save - pk: {blog.pk}")
    blog.save()
    print(f"After save - pk: {blog.pk}")
    print(f"Blog created: {blog}")
    
    # Method 2: Create in one step
    print("\n--- Method 2: Create in one step ---")
    author = Author.objects.create(
        name="New Author",
        email="new.author@example.com"
    )
    print(f"Author created: {author} (pk: {author.pk})")
    
    # Method 3: get_or_create
    print("\n--- Method 3: get_or_create ---")
    category, created = Category.objects.get_or_create(
        name="New Category",
        defaults={'description': 'A new category'}
    )
    print(f"Category: {category}, Created: {created}")
    
    # Try again - should not create
    category2, created2 = Category.objects.get_or_create(
        name="New Category",
        defaults={'description': 'Another description'}
    )
    print(f"Category: {category2}, Created: {created2}")
    
    # Method 4: update_or_create
    print("\n--- Method 4: update_or_create ---")
    mfg, created = Manufacturer.objects.update_or_create(
        name="Test Manufacturer",
        defaults={
            'country': 'USA',
            'founded_year': 2020,
            'website': 'https://test.com'
        }
    )
    print(f"Manufacturer: {mfg}, Created: {created}")


def test_retrieving_objects():
    """Test various ways to retrieve objects."""
    print_section("2. Retrieving Objects")
    
    # Get all objects
    print("\n--- Retrieving all objects ---")
    all_blogs = Blog.objects.all()
    print(f"All blogs count: {all_blogs.count()}")
    print(f"All blogs: {list(all_blogs)}")
    
    # Get single object
    print("\n--- Retrieving single object with get() ---")
    try:
        first_blog = Blog.objects.get(pk=1)
        print(f"First blog: {first_blog}")
    except Blog.DoesNotExist:
        print("Blog with pk=1 does not exist")
    except Blog.MultipleObjectsReturned:
        print("Multiple blogs found")
    
    # Filter objects
    print("\n--- Filtering objects ---")
    tech_blogs = Blog.objects.filter(name__icontains='tech')
    print(f"Tech blogs: {list(tech_blogs)}")
    
    # Exclude objects
    print("\n--- Excluding objects ---")
    non_tech_blogs = Blog.objects.exclude(name__icontains='tech')
    print(f"Non-tech blogs: {list(non_tech_blogs)}")
    
    # Chaining filters
    print("\n--- Chaining filters ---")
    recent_entries = Entry.objects.filter(
        blog__name__icontains='tech'
    ).filter(
        pub_date__gte=date.today() - timedelta(days=10)
    ).exclude(
        rating__lt=3
    )
    print(f"Recent tech entries with rating >= 3: {recent_entries.count()}")
    
    # First and last
    print("\n--- First and last ---")
    first_entry = Entry.objects.first()
    last_entry = Entry.objects.last()
    print(f"First entry: {first_entry}")
    print(f"Last entry: {last_entry}")
    
    # Get with fallback
    print("\n--- Get with fallback ---")
    try:
        entry = Entry.objects.get(headline__icontains='nonexistent')
    except Entry.DoesNotExist:
        entry = Entry.objects.first()
        print(f"Fallback to first entry: {entry}")


def test_field_lookups():
    """Test various field lookup types."""
    print_section("3. Field Lookups")
    
    # Exact match
    print("\n--- Exact match ---")
    exact_blogs = Blog.objects.filter(name__exact='Tech Blog')
    print(f"Exact match 'Tech Blog': {list(exact_blogs)}")
    
    # Case-insensitive exact
    print("\n--- Case-insensitive exact ---")
    iexact_blogs = Blog.objects.filter(name__iexact='TECH BLOG')
    print(f"Case-insensitive 'TECH BLOG': {list(iexact_blogs)}")
    
    # Contains
    print("\n--- Contains ---")
    contains_entries = Entry.objects.filter(headline__contains='Article')
    print(f"Headlines containing 'Article': {contains_entries.count()}")
    
    # Case-insensitive contains
    print("\n--- Case-insensitive contains ---")
    icontains_entries = Entry.objects.filter(headline__icontains='ARTICLE')
    print(f"Headlines containing 'ARTICLE' (case-insensitive): {icontains_entries.count()}")
    
    # Starts with / ends with
    print("\n--- Starts with / ends with ---")
    starts_entries = Entry.objects.filter(headline__startswith='Article')
    ends_entries = Entry.objects.filter(headline__endswith='Content')
    print(f"Headlines starting with 'Article': {starts_entries.count()}")
    print(f"Headlines ending with 'Content': {ends_entries.count()}")
    
    # Greater than / less than
    print("\n--- Comparison operators ---")
    high_rated = Entry.objects.filter(rating__gt=4)
    low_comments = Entry.objects.filter(number_of_comments__lt=5)
    print(f"High rated entries (>4): {high_rated.count()}")
    print(f"Low comment entries (<5): {low_comments.count()}")
    
    # Date lookups
    print("\n--- Date lookups ---")
    recent_entries = Entry.objects.filter(pub_date__gte=date.today() - timedelta(days=7))
    this_year_entries = Entry.objects.filter(pub_date__year=date.today().year)
    print(f"Recent entries (last 7 days): {recent_entries.count()}")
    print(f"This year entries: {this_year_entries.count()}")
    
    # In lookup
    print("\n--- In lookup ---")
    specific_ratings = Entry.objects.filter(rating__in=[4, 5])
    print(f"Entries with rating 4 or 5: {specific_ratings.count()}")
    
    # Range lookup
    print("\n--- Range lookup ---")
    mid_range_comments = Entry.objects.filter(number_of_comments__range=(5, 15))
    print(f"Entries with 5-15 comments: {mid_range_comments.count()}")
    
    # Null lookups
    print("\n--- Null lookups ---")
    authors_with_birthdate = Author.objects.filter(birth_date__isnull=False)
    authors_without_birthdate = Author.objects.filter(birth_date__isnull=True)
    print(f"Authors with birth date: {authors_with_birthdate.count()}")
    print(f"Authors without birth date: {authors_without_birthdate.count()}")


def test_relationship_queries():
    """Test queries spanning relationships."""
    print_section("4. Relationship Queries")
    
    # Forward relationship (ForeignKey)
    print("\n--- Forward relationship queries ---")
    tech_entries = Entry.objects.filter(blog__name='Tech Blog')
    print(f"Entries in Tech Blog: {tech_entries.count()}")
    
    # Reverse relationship
    print("\n--- Reverse relationship queries ---")
    blogs_with_entries = Blog.objects.filter(entry__isnull=False).distinct()
    print(f"Blogs with entries: {blogs_with_entries.count()}")
    
    # Deep relationship spanning
    print("\n--- Deep relationship spanning ---")
    entries_by_john = Entry.objects.filter(authors__name__icontains='John')
    print(f"Entries by authors named John: {entries_by_john.count()}")
    
    # Many-to-many relationships
    print("\n--- Many-to-many relationships ---")
    prolific_authors = Author.objects.filter(entry__number_of_comments__gt=10).distinct()
    print(f"Authors with entries having >10 comments: {prolific_authors.count()}")
    
    # Multiple conditions on same relationship
    print("\n--- Multiple conditions on same relationship ---")
    # Same entry must satisfy both conditions
    specific_entries = Entry.objects.filter(
        authors__name__icontains='John',
        authors__email__icontains='john'
    )
    print(f"Entries by John (same author): {specific_entries.count()}")
    
    # Different entries can satisfy different conditions
    broad_entries = Entry.objects.filter(
        authors__name__icontains='John'
    ).filter(
        authors__email__icontains='jane'
    ).distinct()
    print(f"Entries by John OR Jane (different authors): {broad_entries.count()}")


def test_f_expressions():
    """Test F expressions for field references."""
    print_section("5. F Expressions")
    
    # Compare fields within same model
    print("\n--- Comparing fields within same model ---")
    high_engagement = Entry.objects.filter(number_of_comments__gt=F('number_of_pingbacks'))
    print(f"Entries with more comments than pingbacks: {high_engagement.count()}")
    
    # Arithmetic with F expressions
    print("\n--- Arithmetic with F expressions ---")
    double_pingbacks = Entry.objects.filter(number_of_comments__gt=F('number_of_pingbacks') * 2)
    print(f"Entries with comments > 2x pingbacks: {double_pingbacks.count()}")
    
    # F expressions across relationships
    print("\n--- F expressions across relationships ---")
    # Find products cheaper than their category suggests (if we had category pricing)
    products = Product.objects.all()[:3]
    for product in products:
        print(f"Product: {product.name}, Price: ${product.price}")
    
    # Date arithmetic with F expressions
    print("\n--- Date arithmetic with F expressions ---")
    entries_modified_recently = Entry.objects.filter(
        mod_date__gte=F('pub_date') + timedelta(days=1)
    )
    print(f"Entries modified after publication: {entries_modified_recently.count()}")
    
    # Update using F expressions (atomic operations)
    print("\n--- Updating with F expressions ---")
    print("Incrementing all entry comment counts by 1...")
    updated_count = Entry.objects.update(number_of_comments=F('number_of_comments') + 1)
    print(f"Updated {updated_count} entries")
    
    # Verify the update
    entry = Entry.objects.first()
    print(f"First entry now has {entry.number_of_comments} comments")


def test_q_objects():
    """Test complex queries with Q objects."""
    print_section("6. Q Objects for Complex Queries")
    
    # Basic Q object
    print("\n--- Basic Q object ---")
    q_tech = Q(blog__name__icontains='tech')
    tech_entries = Entry.objects.filter(q_tech)
    print(f"Tech entries using Q object: {tech_entries.count()}")
    
    # OR queries
    print("\n--- OR queries with Q objects ---")
    tech_or_food = Entry.objects.filter(
        Q(blog__name__icontains='tech') | Q(blog__name__icontains='food')
    )
    print(f"Tech OR Food entries: {tech_or_food.count()}")
    
    # AND queries (default behavior)
    print("\n--- AND queries with Q objects ---")
    tech_and_recent = Entry.objects.filter(
        Q(blog__name__icontains='tech') & Q(pub_date__gte=date.today() - timedelta(days=10))
    )
    print(f"Tech AND recent entries: {tech_and_recent.count()}")
    
    # NOT queries
    print("\n--- NOT queries with Q objects ---")
    not_tech = Entry.objects.filter(~Q(blog__name__icontains='tech'))
    print(f"Non-tech entries: {not_tech.count()}")
    
    # Complex combinations
    print("\n--- Complex Q object combinations ---")
    complex_query = Entry.objects.filter(
        (Q(blog__name__icontains='tech') | Q(blog__name__icontains='music')) &
        Q(rating__gte=4) &
        ~Q(number_of_comments=0)
    )
    print(f"Complex query result: {complex_query.count()}")
    
    # Q objects with regular filters
    print("\n--- Q objects mixed with regular filters ---")
    mixed_query = Entry.objects.filter(
        Q(blog__name__icontains='tech') | Q(rating__gte=5),
        pub_date__year=date.today().year
    )
    print(f"Mixed query result: {mixed_query.count()}")


def test_aggregation():
    """Test aggregation functions."""
    print_section("7. Aggregation Functions")
    
    # Basic aggregations
    print("\n--- Basic aggregations ---")
    stats = Entry.objects.aggregate(
        total_entries=Count('id'),
        avg_rating=Avg('rating'),
        max_comments=Max('number_of_comments'),
        min_comments=Min('number_of_comments'),
        total_comments=Sum('number_of_comments')
    )
    
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    # Aggregation with filtering
    print("\n--- Aggregation with filtering ---")
    tech_stats = Entry.objects.filter(blog__name__icontains='tech').aggregate(
        count=Count('id'),
        avg_rating=Avg('rating')
    )
    print(f"Tech blog stats: {tech_stats}")
    
    # Group by aggregation
    print("\n--- Group by aggregation ---")
    blog_stats = Blog.objects.annotate(
        entry_count=Count('entry'),
        avg_rating=Avg('entry__rating'),
        total_comments=Sum('entry__number_of_comments')
    ).values('name', 'entry_count', 'avg_rating', 'total_comments')
    
    print("Blog statistics:")
    for blog in blog_stats:
        avg_rating = blog['avg_rating']
        avg_rating_str = f"{avg_rating:.2f}" if avg_rating else "0.00"
        print(f"  {blog['name']}: {blog['entry_count']} entries, "
              f"avg rating: {avg_rating_str}, "
              f"total comments: {blog['total_comments'] or 0}")


def test_annotations():
    """Test annotations and computed fields."""
    print_section("8. Annotations and Computed Fields")
    
    # Simple annotations
    print("\n--- Simple annotations ---")
    entries_with_engagement = Entry.objects.annotate(
        engagement_score=F('number_of_comments') + F('number_of_pingbacks')
    ).order_by('-engagement_score')[:5]
    
    print("Top 5 entries by engagement:")
    for entry in entries_with_engagement:
        print(f"  {entry.headline}: {entry.engagement_score} points")
    
    # Conditional annotations
    print("\n--- Conditional annotations ---")
    entries_with_categories = Entry.objects.annotate(
        category=Case(
            When(rating__gte=5, then=Value('Excellent')),
            When(rating__gte=4, then=Value('Good')),
            When(rating__gte=3, then=Value('Average')),
            default=Value('Poor'),
            output_field=models.CharField()
        )
    )
    
    for entry in entries_with_categories[:5]:
        print(f"  {entry.headline}: {entry.category} (rating: {entry.rating})")
    
    # String annotations
    print("\n--- String annotations ---")
    authors_with_display_name = Author.objects.annotate(
        display_name=Concat('name', Value(' <'), 'email', Value('>'), output_field=models.CharField())
    )
    
    for author in authors_with_display_name[:5]:
        print(f"  {author.display_name}")
    
    # Date annotations
    print("\n--- Date annotations ---")
    entries_with_year = Entry.objects.annotate(
        pub_year=Extract('pub_date', 'year'),
        pub_month=Extract('pub_date', 'month')
    ).values('headline', 'pub_year', 'pub_month')[:5]
    
    for entry in entries_with_year:
        print(f"  {entry['headline']}: {entry['pub_year']}-{entry['pub_month']:02d}")


def test_slicing_and_pagination():
    """Test QuerySet slicing and pagination."""
    print_section("9. Slicing and Pagination")
    
    # Basic slicing
    print("\n--- Basic slicing ---")
    first_5_entries = Entry.objects.all()[:5]
    print(f"First 5 entries: {[e.headline for e in first_5_entries]}")
    
    # Offset slicing
    print("\n--- Offset slicing ---")
    entries_6_to_10 = Entry.objects.all()[5:10]
    print(f"Entries 6-10: {[e.headline for e in entries_6_to_10]}")
    
    # Step slicing (forces evaluation)
    print("\n--- Step slicing ---")
    every_second_entry = Entry.objects.all()[:10:2]
    print(f"Every 2nd entry (first 10): {[e.headline for e in every_second_entry]}")
    
    # Get specific index
    print("\n--- Get specific index ---")
    try:
        third_entry = Entry.objects.order_by('headline')[2]
        print(f"Third entry (by headline): {third_entry.headline}")
    except IndexError:
        print("Not enough entries")
    
    # Pagination pattern
    print("\n--- Pagination pattern ---")
    page_size = 3
    page_number = 2
    
    total_count = Entry.objects.count()
    total_pages = (total_count + page_size - 1) // page_size
    
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    
    page_entries = Entry.objects.all()[start_index:end_index]
    
    print(f"Page {page_number} of {total_pages} (showing {len(page_entries)} of {total_count}):")
    for entry in page_entries:
        print(f"  {entry.headline}")


def test_queryset_methods():
    """Test various QuerySet methods."""
    print_section("10. QuerySet Methods")
    
    # Exists
    print("\n--- exists() method ---")
    has_tech_entries = Entry.objects.filter(blog__name__icontains='tech').exists()
    print(f"Has tech entries: {has_tech_entries}")
    
    # Count
    print("\n--- count() method ---")
    total_entries = Entry.objects.count()
    tech_entries_count = Entry.objects.filter(blog__name__icontains='tech').count()
    print(f"Total entries: {total_entries}")
    print(f"Tech entries: {tech_entries_count}")
    
    # Distinct
    print("\n--- distinct() method ---")
    all_authors = Author.objects.count()
    authors_with_entries = Author.objects.filter(entry__isnull=False).count()
    unique_authors_with_entries = Author.objects.filter(entry__isnull=False).distinct().count()
    print(f"All authors: {all_authors}")
    print(f"Author-entry relationships: {authors_with_entries}")
    print(f"Unique authors with entries: {unique_authors_with_entries}")
    
    # Values and values_list
    print("\n--- values() and values_list() methods ---")
    blog_names = Blog.objects.values('name', 'tagline')
    print("Blog values:")
    for blog in blog_names:
        print(f"  {blog['name']}: {blog['tagline']}")
    
    author_names = Author.objects.values_list('name', flat=True)
    print(f"Author names: {list(author_names)}")
    
    author_name_emails = Author.objects.values_list('name', 'email')
    print("Author name-email pairs:")
    for name, email in author_name_emails:
        print(f"  {name}: {email}")
    
    # Order by
    print("\n--- order_by() method ---")
    recent_entries = Entry.objects.order_by('-pub_date', 'headline')[:5]
    print("Recent entries (by date desc, then headline):")
    for entry in recent_entries:
        print(f"  {entry.pub_date}: {entry.headline}")
    
    # Reverse
    print("\n--- reverse() method ---")
    oldest_entries = Entry.objects.order_by('-pub_date').reverse()[:3]
    print("Oldest entries:")
    for entry in oldest_entries:
        print(f"  {entry.pub_date}: {entry.headline}")


def test_queryset_optimization():
    """Test QuerySet optimization techniques."""
    print_section("11. QuerySet Optimization")
    
    # select_related for ForeignKey
    print("\n--- select_related() for ForeignKey ---")
    print("Without select_related (will cause N+1 queries):")
    entries = Entry.objects.all()[:3]
    for entry in entries:
        print(f"  {entry.headline} in {entry.blog.name}")
    
    print("\nWith select_related (single query):")
    entries_optimized = Entry.objects.select_related('blog')[:3]
    for entry in entries_optimized:
        print(f"  {entry.headline} in {entry.blog.name}")
    
    # prefetch_related for ManyToMany
    print("\n--- prefetch_related() for ManyToMany ---")
    print("With prefetch_related:")
    entries_with_authors = Entry.objects.prefetch_related('authors')[:3]
    for entry in entries_with_authors:
        author_names = [author.name for author in entry.authors.all()]
        print(f"  {entry.headline} by: {', '.join(author_names)}")
    
    # only() for specific fields
    print("\n--- only() for specific fields ---")
    entry_titles = Entry.objects.only('headline', 'rating')[:3]
    for entry in entry_titles:
        print(f"  {entry.headline} (rating: {entry.rating})")
    
    # defer() to exclude fields
    print("\n--- defer() to exclude fields ---")
    entries_no_body = Entry.objects.defer('body_text')[:3]
    for entry in entries_no_body:
        print(f"  {entry.headline} - {len(entry.body_text)} chars")  # This will hit DB
    
    # QuerySet caching
    print("\n--- QuerySet caching behavior ---")
    print("Creating QuerySet (no DB hit)...")
    qs = Entry.objects.filter(rating__gte=4)
    
    print("First evaluation (hits DB)...")
    count1 = len(list(qs))
    
    print("Second evaluation (uses cache)...")
    count2 = len(list(qs))
    
    print(f"Both evaluations returned {count1} and {count2} entries")


def test_updating_objects():
    """Test updating objects."""
    print_section("12. Updating Objects")
    
    # Update single object
    print("\n--- Updating single object ---")
    entry = Entry.objects.first()
    old_rating = entry.rating
    entry.rating = 5
    entry.save()
    print(f"Updated entry rating from {old_rating} to {entry.rating}")
    
    # Bulk update
    print("\n--- Bulk update ---")
    updated_count = Entry.objects.filter(rating__lt=4).update(rating=4)
    print(f"Updated {updated_count} entries to minimum rating of 4")
    
    # Update with F expressions
    print("\n--- Update with F expressions ---")
    Entry.objects.filter(blog__name__icontains='tech').update(
        number_of_comments=F('number_of_comments') + 5
    )
    print("Added 5 comments to all tech blog entries")
    
    # Conditional update
    print("\n--- Conditional update ---")
    Entry.objects.update(
        rating=Case(
            When(number_of_comments__gt=20, then=Value(5)),
            When(number_of_comments__gt=10, then=Value(4)),
            default=F('rating')
        )
    )
    print("Updated ratings based on comment count")


def test_deleting_objects():
    """Test deleting objects."""
    print_section("13. Deleting Objects")
    
    # Create test data for deletion
    test_blog = Blog.objects.create(name="Test Blog for Deletion", tagline="Will be deleted")
    test_entry = Entry.objects.create(
        blog=test_blog,
        headline="Test Entry for Deletion",
        body_text="This will be deleted",
        pub_date=date.today()
    )
    
    # Delete single object
    print("\n--- Deleting single object ---")
    result = test_entry.delete()
    print(f"Deleted entry: {result}")
    
    # Bulk delete
    print("\n--- Bulk delete ---")
    # Create multiple test entries
    for i in range(3):
        Entry.objects.create(
            blog=test_blog,
            headline=f"Bulk Delete Test {i+1}",
            body_text="For bulk deletion",
            pub_date=date.today()
        )
    
    result = Entry.objects.filter(blog=test_blog).delete()
    print(f"Bulk deleted entries: {result}")
    
    # Delete the test blog
    test_blog.delete()
    print("Deleted test blog")


def test_related_object_access():
    """Test accessing related objects."""
    print_section("14. Related Object Access")
    
    # Forward relationship (ForeignKey)
    print("\n--- Forward relationship access ---")
    entry = Entry.objects.select_related('blog').first()
    print(f"Entry: {entry.headline}")
    print(f"Blog: {entry.blog.name}")
    
    # Reverse relationship (one-to-many)
    print("\n--- Reverse relationship access ---")
    blog = Blog.objects.prefetch_related('entry_set').first()
    print(f"Blog: {blog.name}")
    print(f"Entries count: {blog.entry_set.count()}")
    for entry in blog.entry_set.all()[:3]:
        print(f"  - {entry.headline}")
    
    # Many-to-many relationship
    print("\n--- Many-to-many relationship access ---")
    entry = Entry.objects.prefetch_related('authors').first()
    print(f"Entry: {entry.headline}")
    print("Authors:")
    for author in entry.authors.all():
        print(f"  - {author.name}")
    
    # Reverse many-to-many
    print("\n--- Reverse many-to-many access ---")
    author = Author.objects.prefetch_related('entry_set').first()
    print(f"Author: {author.name}")
    print("Entries:")
    for entry in author.entry_set.all()[:3]:
        print(f"  - {entry.headline}")
    
    # Related managers
    print("\n--- Related manager methods ---")
    blog = Blog.objects.first()
    
    # Count related objects
    entry_count = blog.entry_set.count()
    print(f"Blog has {entry_count} entries")
    
    # Filter related objects
    high_rated_entries = blog.entry_set.filter(rating__gte=4)
    print(f"Blog has {high_rated_entries.count()} high-rated entries")
    
    # Create related objects
    new_entry = blog.entry_set.create(
        headline="Created via related manager",
        body_text="This entry was created using the related manager",
        pub_date=date.today()
    )
    print(f"Created new entry: {new_entry.headline}")


def test_json_field_queries():
    """Test JSON field queries if products have specifications."""
    print_section("15. JSON Field Queries")
    
    # Create products with JSON specifications if none exist
    if not Product.objects.filter(specifications__isnull=False).exists():
        product = Product.objects.first()
        if product:
            product.specifications = {
                'color': 'black',
                'weight': '500g',
                'dimensions': {'height': 10, 'width': 5, 'depth': 2},
                'features': ['wireless', 'waterproof', 'fast-charging']
            }
            product.save()
    
    # Key lookup
    print("\n--- JSON key lookups ---")
    products_with_color = Product.objects.filter(specifications__color__isnull=False)
    print(f"Products with color specification: {products_with_color.count()}")
    
    # Exact value lookup
    print("\n--- JSON exact value lookup ---")
    black_products = Product.objects.filter(specifications__color='black')
    print(f"Black products: {black_products.count()}")
    
    # Nested key lookup
    print("\n--- JSON nested key lookup ---")
    products_with_height = Product.objects.filter(specifications__dimensions__height__isnull=False)
    print(f"Products with height specification: {products_with_height.count()}")
    
    # Array contains (not supported in SQLite)
    print("\n--- JSON array contains ---")
    try:
        wireless_products = Product.objects.filter(specifications__features__contains=['wireless'])
        print(f"Wireless products: {wireless_products.count()}")
    except Exception as e:
        print(f"Array contains not supported: {e}")
    
    # Has key
    print("\n--- JSON has_key lookup ---")
    try:
        products_with_features = Product.objects.filter(specifications__has_key='features')
        print(f"Products with features: {products_with_features.count()}")
    except Exception as e:
        print(f"Has key lookup not supported: {e}")


def test_advanced_queries():
    """Test advanced query patterns."""
    print_section("16. Advanced Query Patterns")
    
    # Subqueries
    print("\n--- Subqueries ---")
    from django.db.models import OuterRef, Subquery
    
    # Find blogs with their latest entry
    latest_entries = Entry.objects.filter(
        blog=OuterRef('pk')
    ).order_by('-pub_date')
    
    blogs_with_latest = Blog.objects.annotate(
        latest_entry_headline=Subquery(latest_entries.values('headline')[:1])
    )
    
    for blog in blogs_with_latest:
        print(f"Blog: {blog.name}, Latest: {blog.latest_entry_headline}")
    
    # Window functions (if supported)
    print("\n--- Ranking (if supported) ---")
    try:
        from django.db.models import Window, RowNumber
        
        ranked_entries = Entry.objects.annotate(
            rank=Window(
                expression=RowNumber(),
                order_by=F('rating').desc()
            )
        ).order_by('rank')[:5]
        
        print("Top 5 entries by rating:")
        for entry in ranked_entries:
            print(f"  Rank {entry.rank}: {entry.headline} (rating: {entry.rating})")
    except ImportError:
        print("Window functions not available in this Django version")
    
    # Complex aggregation
    print("\n--- Complex aggregation ---")
    blog_analytics = Blog.objects.annotate(
        total_entries=Count('entry'),
        avg_rating=Avg('entry__rating'),
        total_engagement=Sum(F('entry__number_of_comments') + F('entry__number_of_pingbacks')),
        best_rating=Max('entry__rating')
    ).filter(total_entries__gt=0)
    
    print("Blog analytics:")
    for blog in blog_analytics:
        avg_rating = blog.avg_rating
        avg_rating_str = f"{avg_rating:.2f}" if avg_rating else "0.00"
        print(f"  {blog.name}:")
        print(f"    Entries: {blog.total_entries}")
        print(f"    Avg Rating: {avg_rating_str}")
        print(f"    Total Engagement: {blog.total_engagement or 0}")
        print(f"    Best Rating: {blog.best_rating}")


def main():
    """Main test function."""
    print("Django Database Queries Comprehensive Practice")
    print("Following https://docs.djangoproject.com/en/5.2/topics/db/queries/")
    
    try:
        # Setup sample data
        setup_sample_data()
        
        # Run all tests
        test_creating_objects()
        test_retrieving_objects()
        test_field_lookups()
        test_relationship_queries()
        test_f_expressions()
        test_q_objects()
        test_aggregation()
        test_annotations()
        test_slicing_and_pagination()
        test_queryset_methods()
        test_queryset_optimization()
        test_updating_objects()
        test_deleting_objects()
        test_related_object_access()
        test_json_field_queries()
        test_advanced_queries()
        
        print_section("Summary")
        print("✅ All Django database query concepts demonstrated successfully!")
        print("\nKey concepts covered:")
        print("- Creating objects: save(), create(), get_or_create(), update_or_create()")
        print("- Retrieving objects: all(), get(), filter(), exclude(), first(), last()")
        print("- Field lookups: exact, iexact, contains, icontains, startswith, endswith")
        print("- Comparison operators: gt, gte, lt, lte, in, range")
        print("- Date/time lookups: year, month, day, date, time")
        print("- Null lookups: isnull")
        print("- Relationship queries: forward, reverse, spanning relationships")
        print("- F expressions: field references, arithmetic, cross-relationship")
        print("- Q objects: OR, AND, NOT, complex combinations")
        print("- Aggregation: Count, Sum, Avg, Max, Min")
        print("- Annotations: computed fields, conditional logic")
        print("- QuerySet methods: exists(), count(), distinct(), values(), values_list()")
        print("- Slicing and pagination: [start:end], [start:end:step]")
        print("- Optimization: select_related(), prefetch_related(), only(), defer()")
        print("- Updates: single object, bulk update, F expressions")
        print("- Deletion: single object, bulk delete")
        print("- Related object access: forward, reverse, managers")
        print("- JSON field queries: key lookups, nested access, array operations")
        print("- Advanced patterns: subqueries, window functions, complex aggregation")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
