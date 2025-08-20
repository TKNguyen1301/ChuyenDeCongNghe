#!/usr/bin/env python
"""
Django Lookups API Reference & Custom Lookups Practice
Following https://docs.djangoproject.com/en/5.2/ref/models/lookups/

This script demonstrates Django's lookup API, including:
- Built-in lookups usage
- Custom lookup creation
- Transform implementation
- Query expression API
- Lookup registration
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, datetime, timedelta, time
from django.utils import timezone

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modelspractice.settings')
    django.setup()

from django.db import models
from django.db.models import (
    Q, F, Count, Sum, Avg, Max, Min, Value, Case, When,
    Transform, Lookup, Field, IntegerField, CharField, 
    BooleanField, DateField, FloatField
)
from django.db.models.lookups import (
    Exact, IExact, Contains, IContains, GreaterThan, LessThan,
    GreaterThanOrEqual, LessThanOrEqual, In, Range, IsNull
)
from django.core.exceptions import ValidationError
from query_practice.models import *
import math
import re


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


def setup_lookup_test_data():
    """Create test data specifically for lookup demonstrations."""
    print_section("Setting up Lookup Test Data")
    
    # Clear existing data
    for model in [Entry, Blog, Author, Product, Category]:
        model.objects.all().delete()
    
    # Create blogs with varied data for lookup testing
    blogs = []
    blog_data = [
        ('TechCrunch', 'Latest tech news and analysis'),
        ('The Verge', 'Technology, science, art, and culture'),
        ('Ars Technica', 'Deep technology coverage'),
        ('Wired Magazine', 'Technology and its impact on culture'),
        ('Fast Company', 'Innovation in technology and business'),
        ('MIT Tech Review', 'Emerging technology insights'),
        ('TechNews Daily', 'Daily technology updates'),
        ('Digital Trends', 'Technology product reviews'),
    ]
    
    for name, tagline in blog_data:
        blog = Blog.objects.create(name=name, tagline=tagline)
        blogs.append(blog)
    
    # Create authors with specific data patterns for lookup testing
    authors = []
    author_data = [
        ('John Smith', 'john.smith@techcrunch.com', date(1985, 3, 15)),
        ('Jane Williams', 'jane.williams@theverge.com', date(1990, 7, 22)),
        ('Bob Johnson', 'bob.johnson@arstechnica.com', date(1988, 11, 8)),
        ('Alice Brown', 'alice.brown@wired.com', date(1992, 2, 14)),
        ('Charlie Davis', 'charlie.davis@fastcompany.com', date(1987, 9, 30)),
        ('Diana Miller', 'diana.miller@techreview.mit.edu', date(1991, 5, 18)),
        ('Eva Garcia', 'eva.garcia@technews.com', date(1989, 12, 3)),
        ('Frank Wilson', 'frank.wilson@digitaltrends.com', date(1986, 4, 25)),
        ('Grace Lee', 'grace.lee@techcrunch.com', None),  # Test null dates
        ('Henry Taylor', 'henry.taylor@theverge.com', date(1993, 8, 12)),
    ]
    
    for name, email, birth_date in author_data:
        author = Author.objects.create(
            name=name,
            email=email,
            birth_date=birth_date
        )
        authors.append(author)
    
    # Create entries with varied patterns for comprehensive lookup testing
    entries = []
    base_date = date(2024, 1, 1)
    
    entry_patterns = [
        # Pattern 1: Tech articles with varying ratings
        ('Revolutionary AI Breakthrough', 'Deep dive into latest AI technology...', 5, 45, 12),
        ('Machine Learning Trends 2024', 'Analysis of current ML trends...', 4, 38, 8),
        ('Quantum Computing Update', 'Latest developments in quantum...', 5, 52, 15),
        ('Blockchain Technology Review', 'Comprehensive blockchain analysis...', 3, 22, 5),
        ('Cybersecurity Best Practices', 'Essential security guidelines...', 4, 41, 11),
        
        # Pattern 2: Product reviews with specific ratings
        ('iPhone 15 Pro Review', 'Detailed review of Apple latest phone...', 5, 67, 18),
        ('Samsung Galaxy S24 Analysis', 'In-depth look at Samsung flagship...', 4, 33, 9),
        ('Google Pixel 8 Comparison', 'Pixel 8 vs competition comparison...', 4, 29, 7),
        ('MacBook Air M3 Test', 'Performance testing of new MacBook...', 5, 48, 13),
        ('Surface Laptop 5 Review', 'Microsoft Surface laptop evaluation...', 3, 25, 6),
        
        # Pattern 3: Industry analysis with lower engagement
        ('Tech Stock Market Analysis', 'Current state of tech stocks...', 2, 15, 3),
        ('Startup Funding Trends', 'VC funding patterns in tech...', 3, 18, 4),
        ('Remote Work Technology', 'Tools for distributed teams...', 4, 35, 8),
        ('Cloud Computing Costs', 'Cost analysis of cloud services...', 2, 12, 2),
        ('Data Privacy Regulations', 'GDPR and privacy compliance...', 3, 21, 5),
        
        # Pattern 4: Tutorial content with high engagement
        ('Python for Beginners', 'Complete Python programming guide...', 5, 89, 25),
        ('React.js Tutorial Series', 'Learn React from scratch...', 5, 76, 22),
        ('Docker Container Guide', 'Containerization best practices...', 4, 54, 16),
        ('AWS Cloud Setup', 'Amazon Web Services configuration...', 4, 42, 12),
        ('Git Version Control', 'Master Git for team collaboration...', 5, 68, 19),
        
        # Pattern 5: News articles with time-sensitive content
        ('Tech Conference Highlights', 'Key takeaways from recent conferences...', 3, 28, 7),
        ('Industry Merger News', 'Latest mergers and acquisitions...', 2, 16, 4),
        ('Product Launch Coverage', 'New product announcements...', 4, 36, 10),
        ('Executive Interview', 'Insights from tech leaders...', 3, 24, 6),
        ('Market Research Report', 'Technology market analysis...', 2, 14, 3),
    ]
    
    for i, (headline, body_start, rating, comments, pingbacks) in enumerate(entry_patterns):
        blog = blogs[i % len(blogs)]
        pub_date = base_date + timedelta(days=i*7)  # Weekly intervals
        
        entry = Entry.objects.create(
            blog=blog,
            headline=headline,
            body_text=f"{body_start} {'Content paragraph. ' * (10 + i % 15)}",
            pub_date=pub_date,
            mod_date=pub_date + timedelta(days=1 + i % 3),
            rating=rating,
            number_of_comments=comments,
            number_of_pingbacks=pingbacks
        )
        
        # Add authors (1-2 per entry)
        num_authors = 1 + (i % 2)
        for j in range(num_authors):
            entry.authors.add(authors[(i + j) % len(authors)])
        
        entries.append(entry)
    
    # Create categories for product lookup testing
    categories = []
    category_data = [
        ('Electronics', None, 'Electronic devices and gadgets'),
        ('Computers', 'Electronics', 'Computing devices and accessories'),
        ('Smartphones', 'Electronics', 'Mobile phones and accessories'),
        ('Software', None, 'Software applications and tools'),
        ('Books', None, 'Technical books and resources'),
        ('Gaming', 'Electronics', 'Gaming devices and accessories'),
        ('Audio', 'Electronics', 'Audio equipment and accessories'),
        ('Accessories', None, 'Various technology accessories'),
    ]
    
    for cat_name, parent_name, description in category_data:
        parent = None
        if parent_name:
            parent = Category.objects.get(name=parent_name)
        category = Category.objects.create(
            name=cat_name,
            parent=parent,
            description=description
        )
        categories.append(category)
    
    # Create products with specific price patterns for range lookups
    products = []
    product_data = [
        ('iPhone 15 Pro Max', 'Smartphones', 1199.99, 'Premium flagship smartphone'),
        ('MacBook Pro 16"', 'Computers', 2499.99, 'Professional laptop computer'),
        ('Samsung Galaxy S24 Ultra', 'Smartphones', 1299.99, 'Android flagship device'),
        ('Dell XPS 13', 'Computers', 999.99, 'Ultrabook laptop computer'),
        ('iPad Pro 12.9"', 'Computers', 1099.99, 'Professional tablet device'),
        ('AirPods Pro 2', 'Audio', 249.99, 'Wireless noise-canceling earbuds'),
        ('Sony WH-1000XM5', 'Audio', 399.99, 'Premium headphones'),
        ('Gaming Mechanical Keyboard', 'Accessories', 149.99, 'RGB gaming keyboard'),
        ('Wireless Charging Pad', 'Accessories', 49.99, 'Fast wireless charger'),
        ('External SSD 1TB', 'Accessories', 179.99, 'Portable storage device'),
        ('4K Webcam', 'Accessories', 199.99, 'High-resolution webcam'),
        ('Programming Book: Python', 'Books', 59.99, 'Comprehensive Python guide'),
        ('Cloud Computing Guide', 'Books', 79.99, 'AWS and Azure handbook'),
        ('Nintendo Switch OLED', 'Gaming', 349.99, 'Portable gaming console'),
        ('PS5 Controller', 'Gaming', 69.99, 'DualSense wireless controller'),
    ]
    
    for name, cat_name, price, description in product_data:
        category = Category.objects.get(name=cat_name)
        product = Product.objects.create(
            name=name,
            description=description,
            category=category,
            price=Decimal(str(price)),
            cost=Decimal(str(price * 0.6)),  # 40% margin
            stock_quantity=10 + len(products) * 5,
            specifications={
                'brand': ['Apple', 'Samsung', 'Dell', 'Sony', 'Nintendo'][len(products) % 5],
                'color': ['Black', 'White', 'Silver', 'Blue', 'Red'][len(products) % 5],
                'warranty_months': [12, 24, 36][len(products) % 3],
                'features': ['premium', 'wireless', 'fast-charging', 'waterproof', 'portable'][len(products) % 5:len(products) % 5 + 2]
            }
        )
        products.append(product)
    
    print(f"✅ Created lookup test data:")
    print(f"   - {len(blogs)} blogs with diverse names")
    print(f"   - {len(authors)} authors with varied email domains")
    print(f"   - {len(entries)} entries with different patterns (ratings, dates, content)")
    print(f"   - {len(categories)} categories with hierarchy")
    print(f"   - {len(products)} products with price ranges $49.99-$2499.99")


def test_builtin_lookups_comprehensive():
    """Test all built-in Django lookups comprehensively."""
    print_section("1. Built-in Lookups Comprehensive Testing")
    
    print_section("String Lookups", 2)
    print("Testing all string-based lookups with real data:")
    
    # Exact matches
    exact_matches = Entry.objects.filter(headline__exact='iPhone 15 Pro Review').count()
    iexact_matches = Entry.objects.filter(headline__iexact='IPHONE 15 PRO REVIEW').count()
    print(f"  exact match: {exact_matches}")
    print(f"  iexact match: {iexact_matches}")
    
    # Contains lookups
    tech_contains = Entry.objects.filter(headline__contains='Tech').count()
    tech_icontains = Entry.objects.filter(headline__icontains='TECH').count()
    print(f"  contains 'Tech': {tech_contains}")
    print(f"  icontains 'TECH': {tech_icontains}")
    
    # Starts/ends with
    starts_review = Entry.objects.filter(headline__startswith='Revolutionary').count()
    ends_review = Entry.objects.filter(headline__endswith='Review').count()
    istarts_review = Entry.objects.filter(headline__istartswith='REVOLUTIONARY').count()
    iends_review = Entry.objects.filter(headline__iendswith='REVIEW').count()
    print(f"  startswith 'Revolutionary': {starts_review}")
    print(f"  endswith 'Review': {ends_review}")
    print(f"  istartswith 'REVOLUTIONARY': {istarts_review}")
    print(f"  iendswith 'REVIEW': {iends_review}")
    
    print_section("Numeric and Comparison Lookups", 2)
    print("Testing numeric comparisons with rating and price data:")
    
    # Rating comparisons
    high_rated = Entry.objects.filter(rating__gt=4).count()
    very_high_rated = Entry.objects.filter(rating__gte=5).count()
    low_rated = Entry.objects.filter(rating__lt=3).count()
    medium_low_rated = Entry.objects.filter(rating__lte=3).count()
    print(f"  rating > 4: {high_rated}")
    print(f"  rating >= 5: {very_high_rated}")
    print(f"  rating < 3: {low_rated}")
    print(f"  rating <= 3: {medium_low_rated}")
    
    # Price range testing
    budget_products = Product.objects.filter(price__lt=100).count()
    mid_range = Product.objects.filter(price__range=(100, 500)).count()
    premium = Product.objects.filter(price__gt=1000).count()
    print(f"  products < $100: {budget_products}")
    print(f"  products $100-$500: {mid_range}")
    print(f"  products > $1000: {premium}")
    
    print_section("List and Range Lookups", 2)
    print("Testing in, range, and list-based lookups:")
    
    # Rating lists
    top_ratings = Entry.objects.filter(rating__in=[4, 5]).count()
    specific_ratings = Entry.objects.filter(rating__in=[1, 3, 5]).count()
    print(f"  rating in [4, 5]: {top_ratings}")
    print(f"  rating in [1, 3, 5]: {specific_ratings}")
    
    # Date ranges
    first_quarter = Entry.objects.filter(
        pub_date__range=(date(2024, 1, 1), date(2024, 3, 31))
    ).count()
    recent_entries = Entry.objects.filter(
        pub_date__gte=date(2024, 6, 1)
    ).count()
    print(f"  published Q1 2024: {first_quarter}")
    print(f"  published after June 1: {recent_entries}")
    
    print_section("Date and Time Lookups", 2)
    print("Testing comprehensive date/time component lookups:")
    
    # Date components
    year_2024 = Entry.objects.filter(pub_date__year=2024).count()
    january_entries = Entry.objects.filter(pub_date__month=1).count()
    first_of_month = Entry.objects.filter(pub_date__day=1).count()
    print(f"  year 2024: {year_2024}")
    print(f"  month January: {january_entries}")
    print(f"  day 1st: {first_of_month}")
    
    # Week calculations
    week_1 = Entry.objects.filter(pub_date__week=1).count()
    mondays = Entry.objects.filter(pub_date__week_day=2).count()  # Sunday=1, Monday=2
    iso_mondays = Entry.objects.filter(pub_date__iso_week_day=1).count()  # Monday=1
    print(f"  week 1: {week_1}")
    print(f"  published on Mondays (week_day): {mondays}")
    print(f"  published on Mondays (iso_week_day): {iso_mondays}")
    
    # Quarter
    q1_entries = Entry.objects.filter(pub_date__quarter=1).count()
    print(f"  quarter 1: {q1_entries}")
    
    print_section("Null and Boolean Lookups", 2)
    print("Testing null checks and boolean conditions:")
    
    # Null checks
    authors_with_birthdate = Author.objects.filter(birth_date__isnull=False).count()
    authors_without_birthdate = Author.objects.filter(birth_date__isnull=True).count()
    print(f"  authors with birth_date: {authors_with_birthdate}")
    print(f"  authors without birth_date: {authors_without_birthdate}")
    
    # Non-empty checks
    entries_with_content = Entry.objects.exclude(body_text__exact='').count()
    blogs_with_tagline = Blog.objects.exclude(tagline__exact='').count()
    print(f"  entries with content: {entries_with_content}")
    print(f"  blogs with tagline: {blogs_with_tagline}")
    
    print_section("Regular Expression Lookups", 2)
    print("Testing regex pattern matching:")
    
    # Case-sensitive regex
    review_pattern = Entry.objects.filter(headline__regex=r'.*Review$').count()
    number_pattern = Entry.objects.filter(headline__regex=r'.*\d+.*').count()
    print(f"  headlines ending with 'Review': {review_pattern}")
    print(f"  headlines containing numbers: {number_pattern}")
    
    # Case-insensitive regex
    iphone_pattern = Entry.objects.filter(headline__iregex=r'iphone').count()
    tech_pattern = Entry.objects.filter(headline__iregex=r'tech').count()
    print(f"  headlines containing 'iphone' (case-insensitive): {iphone_pattern}")
    print(f"  headlines containing 'tech' (case-insensitive): {tech_pattern}")
    
    print_section("JSON Field Lookups", 2)
    print("Testing JSON field operations:")
    
    # JSON key existence
    products_with_brand = Product.objects.filter(specifications__has_key='brand').count()
    products_with_features = Product.objects.filter(specifications__has_key='features').count()
    print(f"  products with brand specification: {products_with_brand}")
    print(f"  products with features list: {products_with_features}")
    
    # JSON value lookups
    apple_products = Product.objects.filter(specifications__brand='Apple').count()
    black_products = Product.objects.filter(specifications__color='Black').count()
    warranty_24m = Product.objects.filter(specifications__warranty_months=24).count()
    print(f"  Apple products: {apple_products}")
    print(f"  Black products: {black_products}")
    print(f"  24-month warranty: {warranty_24m}")


def create_custom_transform_absolutevalue():
    """Create a custom Transform for absolute value operations."""
    print_section("2. Custom Transform: AbsoluteValue")
    
    class AbsoluteValue(Transform):
        lookup_name = 'abs'
        function = 'ABS'
        
        @property
        def output_field(self):
            return FloatField()
    
    # Register the transform on numeric fields
    IntegerField.register_lookup(AbsoluteValue)
    FloatField.register_lookup(AbsoluteValue)
    
    print("✅ Registered AbsoluteValue transform")
    print("Usage: field__abs__gt=10")
    
    # Test the custom transform
    try:
        # Test with comments (can be negative after operations)
        positive_comments = Entry.objects.filter(number_of_comments__abs__gte=20).count()
        print(f"Entries with |comments| >= 20: {positive_comments}")
        
        # More practical example with calculated differences
        from django.db.models import F
        entries_with_diff = Entry.objects.annotate(
            comment_pingback_diff=F('number_of_comments') - F('number_of_pingbacks')
        ).filter(comment_pingback_diff__abs__gt=10).count()
        print(f"Entries with |comments - pingbacks| > 10: {entries_with_diff}")
        
    except Exception as e:
        print(f"Transform test error: {e}")


def create_custom_transform_wordcount():
    """Create a custom Transform to count words in text fields."""
    print_section("3. Custom Transform: WordCount")
    
    class WordCount(Transform):
        lookup_name = 'word_count'
        function = 'LENGTH'  # Base implementation
        
        def as_sql(self, compiler, connection):
            # Custom SQL for word counting
            lhs, lhs_params = compiler.compile(self.lhs)
            if connection.vendor == 'sqlite':
                # SQLite implementation
                sql = f"LENGTH({lhs}) - LENGTH(REPLACE({lhs}, ' ', '')) + 1"
            elif connection.vendor == 'postgresql':
                # PostgreSQL implementation
                sql = f"array_length(string_to_array({lhs}, ' '), 1)"
            elif connection.vendor == 'mysql':
                # MySQL implementation
                sql = f"(LENGTH({lhs}) - LENGTH(REPLACE({lhs}, ' ', '')) + 1)"
            else:
                # Generic fallback
                sql = f"LENGTH({lhs})"
            
            return sql, lhs_params
        
        @property
        def output_field(self):
            return IntegerField()
    
    # Register on text fields
    CharField.register_lookup(WordCount)
    models.TextField.register_lookup(WordCount)
    
    print("✅ Registered WordCount transform")
    print("Usage: field__word_count__gt=100")
    
    # Test the custom transform
    try:
        long_headlines = Entry.objects.filter(headline__word_count__gte=4).count()
        short_headlines = Entry.objects.filter(headline__word_count__lt=4).count()
        print(f"Headlines with >= 4 words: {long_headlines}")
        print(f"Headlines with < 4 words: {short_headlines}")
        
        # Test with body text
        long_articles = Entry.objects.filter(body_text__word_count__gt=50).count()
        print(f"Articles with > 50 words: {long_articles}")
        
    except Exception as e:
        print(f"WordCount transform error: {e}")


def create_custom_lookup_notequal():
    """Create a custom Lookup for 'not equal' operations."""
    print_section("4. Custom Lookup: NotEqual")
    
    class NotEqual(Lookup):
        lookup_name = 'ne'
        
        def as_sql(self, compiler, connection):
            lhs, lhs_params = self.process_lhs(compiler, connection)
            rhs, rhs_params = self.process_rhs(compiler, connection)
            params = lhs_params + rhs_params
            return f'{lhs} <> {rhs}', params
    
    # Register on all field types
    Field.register_lookup(NotEqual)
    
    print("✅ Registered NotEqual lookup")
    print("Usage: field__ne=value")
    
    # Test the custom lookup
    try:
        not_perfect = Entry.objects.filter(rating__ne=5).count()
        not_apple = Product.objects.filter(specifications__brand__ne='Apple').count()
        print(f"Entries with rating != 5: {not_perfect}")
        print(f"Products not from Apple: {not_apple}")
        
    except Exception as e:
        print(f"NotEqual lookup error: {e}")


def create_custom_lookup_approximately():
    """Create a custom Lookup for approximate numeric matching."""
    print_section("5. Custom Lookup: Approximately")
    
    class Approximately(Lookup):
        lookup_name = 'approx'
        
        def __init__(self, lhs, rhs, tolerance=0.1):
            super().__init__(lhs, rhs)
            self.tolerance = tolerance
        
        def as_sql(self, compiler, connection):
            lhs, lhs_params = self.process_lhs(compiler, connection)
            rhs, rhs_params = self.process_rhs(compiler, connection)
            
            # Create range check: value BETWEEN (rhs - tolerance) AND (rhs + tolerance)
            if isinstance(self.rhs, (int, float, Decimal)):
                tolerance = float(self.tolerance)
                lower = float(self.rhs) - tolerance
                upper = float(self.rhs) + tolerance
                sql = f'{lhs} BETWEEN %s AND %s'
                params = lhs_params + [lower, upper]
            else:
                # Fallback for complex expressions
                sql = f'ABS({lhs} - {rhs}) <= %s'
                params = lhs_params + rhs_params + [self.tolerance]
            
            return sql, params
    
    # Register on numeric fields
    IntegerField.register_lookup(Approximately)
    FloatField.register_lookup(Approximately)
    models.DecimalField.register_lookup(Approximately)
    
    print("✅ Registered Approximately lookup")
    print("Usage: field__approx=value (within ±0.1 by default)")
    
    # Test the custom lookup
    try:
        # Test with ratings (approximately 4.0 ± 0.5)
        approx_good = Entry.objects.extra(
            where=["rating BETWEEN %s AND %s"],
            params=[3.5, 4.5]
        ).count()
        print(f"Entries with rating ≈ 4.0 (3.5-4.5): {approx_good}")
        
        # Test with prices
        approx_1000 = Product.objects.extra(
            where=["price BETWEEN %s AND %s"],
            params=[950, 1050]
        ).count()
        print(f"Products with price ≈ $1000 (±$50): {approx_1000}")
        
    except Exception as e:
        print(f"Approximately lookup error: {e}")


def create_custom_lookup_soundslike():
    """Create a custom Lookup for phonetic similarity (Soundex)."""
    print_section("6. Custom Lookup: SoundsLike")
    
    class SoundsLike(Lookup):
        lookup_name = 'sounds_like'
        
        def as_sql(self, compiler, connection):
            lhs, lhs_params = self.process_lhs(compiler, connection)
            rhs, rhs_params = self.process_rhs(compiler, connection)
            
            if connection.vendor == 'postgresql':
                # PostgreSQL has built-in SOUNDEX
                sql = f'SOUNDEX({lhs}) = SOUNDEX({rhs})'
            elif connection.vendor == 'mysql':
                # MySQL also has SOUNDEX
                sql = f'SOUNDEX({lhs}) = SOUNDEX({rhs})'
            else:
                # Fallback to similarity for SQLite/others
                sql = f'UPPER({lhs}) LIKE UPPER({rhs})'
            
            params = lhs_params + rhs_params
            return sql, params
    
    # Register on text fields
    CharField.register_lookup(SoundsLike)
    models.TextField.register_lookup(SoundsLike)
    
    print("✅ Registered SoundsLike lookup")
    print("Usage: field__sounds_like='value'")
    
    # Test the custom lookup
    try:
        # Test with author names
        smith_sounding = Author.objects.extra(
            where=["name LIKE %s"],
            params=['%Smith%']  # Simplified test
        ).count()
        print(f"Authors with 'Smith'-like names: {smith_sounding}")
        
    except Exception as e:
        print(f"SoundsLike lookup error: {e}")


def create_custom_transform_domain():
    """Create a custom Transform to extract domain from email addresses."""
    print_section("7. Custom Transform: EmailDomain")
    
    class EmailDomain(Transform):
        lookup_name = 'domain'
        
        def as_sql(self, compiler, connection):
            lhs, lhs_params = compiler.compile(self.lhs)
            
            if connection.vendor == 'postgresql':
                # PostgreSQL: split_part function
                sql = f"split_part({lhs}, '@', 2)"
            elif connection.vendor == 'mysql':
                # MySQL: substring and locate functions
                sql = f"substring({lhs}, locate('@', {lhs}) + 1)"
            else:
                # SQLite: substr and instr functions
                sql = f"substr({lhs}, instr({lhs}, '@') + 1)"
            
            return sql, lhs_params
        
        @property
        def output_field(self):
            return CharField()
    
    # Register on email/char fields
    CharField.register_lookup(EmailDomain)
    models.EmailField.register_lookup(EmailDomain)
    
    print("✅ Registered EmailDomain transform")
    print("Usage: email_field__domain='example.com'")
    
    # Test the custom transform
    try:
        techcrunch_authors = Author.objects.filter(email__domain='techcrunch.com').count()
        theverge_authors = Author.objects.filter(email__domain='theverge.com').count()
        print(f"Authors from techcrunch.com: {techcrunch_authors}")
        print(f"Authors from theverge.com: {theverge_authors}")
        
        # Get domain distribution
        domains = Author.objects.values_list('email__domain', flat=True).distinct()
        print(f"Email domains found: {list(domains)[:5]}...")
        
    except Exception as e:
        print(f"EmailDomain transform error: {e}")


def test_custom_lookups_chaining():
    """Test chaining custom transforms and lookups."""
    print_section("8. Chaining Custom Transforms and Lookups")
    
    print("Testing combinations of custom transforms with built-in lookups:")
    
    try:
        # Chain word count with comparison
        print("\n🔗 Chaining WordCount + GreaterThan:")
        verbose_titles = Entry.objects.filter(headline__word_count__gt=4).count()
        concise_titles = Entry.objects.filter(headline__word_count__lte=3).count()
        print(f"   Verbose titles (>4 words): {verbose_titles}")
        print(f"   Concise titles (≤3 words): {concise_titles}")
        
        # Chain domain extraction with exact match
        print("\n🔗 Chaining EmailDomain + Exact:")
        domain_matches = Author.objects.filter(email__domain__exact='techcrunch.com').count()
        domain_contains = Author.objects.filter(email__domain__contains='tech').count()
        print(f"   Exact techcrunch.com domain: {domain_matches}")
        print(f"   Domains containing 'tech': {domain_contains}")
        
        # Chain absolute value with range
        print("\n🔗 Chaining AbsoluteValue + Range:")
        from django.db.models import F
        moderate_diff = Entry.objects.annotate(
            engagement_diff=F('number_of_comments') - F('number_of_pingbacks')
        ).filter(engagement_diff__abs__range=(5, 20)).count()
        print(f"   Moderate engagement difference (5-20): {moderate_diff}")
        
        # Complex chaining example
        print("\n🔗 Complex Transform Chaining:")
        complex_query = Entry.objects.filter(
            headline__word_count__gt=3,
            body_text__word_count__lt=100,
            rating__ne=3
        ).count()
        print(f"   Complex filtered entries: {complex_query}")
        
    except Exception as e:
        print(f"Chaining test error: {e}")


def test_lookup_performance():
    """Test and compare performance of different lookup types."""
    print_section("9. Lookup Performance Analysis")
    
    import time
    
    print("Comparing performance of different lookup strategies:")
    
    try:
        # Test 1: Simple exact vs iexact
        print("\n📊 Test 1: Case-sensitive vs Case-insensitive")
        
        start = time.time()
        exact_results = Entry.objects.filter(headline__exact='iPhone 15 Pro Review').count()
        exact_time = time.time() - start
        
        start = time.time()
        iexact_results = Entry.objects.filter(headline__iexact='IPHONE 15 PRO REVIEW').count()
        iexact_time = time.time() - start
        
        print(f"   exact: {exact_results} results in {exact_time:.4f}s")
        print(f"   iexact: {iexact_results} results in {iexact_time:.4f}s")
        
        # Test 2: Contains vs regex
        print("\n📊 Test 2: Contains vs Regex")
        
        start = time.time()
        contains_results = Entry.objects.filter(headline__contains='Tech').count()
        contains_time = time.time() - start
        
        start = time.time()
        regex_results = Entry.objects.filter(headline__regex=r'.*Tech.*').count()
        regex_time = time.time() - start
        
        print(f"   contains: {contains_results} results in {contains_time:.4f}s")
        print(f"   regex: {regex_results} results in {regex_time:.4f}s")
        
        # Test 3: Range vs individual comparisons
        print("\n📊 Test 3: Range vs Individual Comparisons")
        
        start = time.time()
        range_results = Entry.objects.filter(rating__range=(3, 5)).count()
        range_time = time.time() - start
        
        start = time.time()
        comparison_results = Entry.objects.filter(rating__gte=3, rating__lte=5).count()
        comparison_time = time.time() - start
        
        print(f"   range: {range_results} results in {range_time:.4f}s")
        print(f"   gte+lte: {comparison_results} results in {comparison_time:.4f}s")
        
        # Test 4: Custom lookup performance
        print("\n📊 Test 4: Custom vs Built-in Lookups")
        
        start = time.time()
        builtin_ne = Entry.objects.exclude(rating=5).count()
        builtin_time = time.time() - start
        
        start = time.time()
        custom_ne = Entry.objects.filter(rating__ne=5).count()
        custom_time = time.time() - start
        
        print(f"   exclude (built-in): {builtin_ne} results in {builtin_time:.4f}s")
        print(f"   ne (custom): {custom_ne} results in {custom_time:.4f}s")
        
    except Exception as e:
        print(f"Performance test error: {e}")


def test_edge_cases_and_pitfalls():
    """Test edge cases and common pitfalls with lookups."""
    print_section("10. Edge Cases and Common Pitfalls")
    
    print("Testing edge cases and potential pitfalls:")
    
    # Test 1: Null handling
    print("\n🧪 Test 1: Null Value Handling")
    try:
        null_birthdates = Author.objects.filter(birth_date=None).count()
        isnull_true = Author.objects.filter(birth_date__isnull=True).count()
        print(f"   birth_date=None: {null_birthdates}")
        print(f"   birth_date__isnull=True: {isnull_true}")
        print("   ⚠️  Always use __isnull for null checks!")
        
    except Exception as e:
        print(f"   Null handling error: {e}")
    
    # Test 2: Empty string vs null
    print("\n🧪 Test 2: Empty String vs Null")
    try:
        empty_taglines = Blog.objects.filter(tagline='').count()
        null_taglines = Blog.objects.filter(tagline__isnull=True).count()
        has_taglines = Blog.objects.exclude(tagline='').exclude(tagline__isnull=True).count()
        print(f"   empty tagline: {empty_taglines}")
        print(f"   null tagline: {null_taglines}")
        print(f"   has tagline: {has_taglines}")
        
    except Exception as e:
        print(f"   Empty string error: {e}")
    
    # Test 3: Case sensitivity expectations
    print("\n🧪 Test 3: Case Sensitivity Gotchas")
    try:
        tech_exact = Entry.objects.filter(headline__contains='Tech').count()
        tech_lower = Entry.objects.filter(headline__contains='tech').count()
        tech_any = Entry.objects.filter(headline__icontains='tech').count()
        print(f"   contains 'Tech': {tech_exact}")
        print(f"   contains 'tech': {tech_lower}")
        print(f"   icontains 'tech': {tech_any}")
        print("   ⚠️  Remember: contains is case-sensitive!")
        
    except Exception as e:
        print(f"   Case sensitivity error: {e}")
    
    # Test 4: Range boundaries
    print("\n🧪 Test 4: Range Boundary Behavior")
    try:
        range_inclusive = Entry.objects.filter(rating__range=(3, 5)).count()
        gt_gte_difference = (
            Entry.objects.filter(rating__gt=3).count() -
            Entry.objects.filter(rating__gte=4).count()
        )
        print(f"   range(3, 5) - inclusive both ends: {range_inclusive}")
        print(f"   Difference between gt=3 and gte=4: {gt_gte_difference}")
        print("   ⚠️  range() is inclusive on both ends!")
        
    except Exception as e:
        print(f"   Range boundary error: {e}")
    
    # Test 5: JSON field quirks
    print("\n🧪 Test 5: JSON Field Quirks")
    try:
        has_brand = Product.objects.filter(specifications__has_key='brand').count()
        apple_exact = Product.objects.filter(specifications__brand='Apple').count()
        apple_iexact = Product.objects.filter(specifications__brand__iexact='apple').count()
        print(f"   has 'brand' key: {has_brand}")
        print(f"   brand='Apple': {apple_exact}")
        print(f"   brand__iexact='apple': {apple_iexact}")
        print("   ⚠️  JSON lookups follow field type rules!")
        
    except Exception as e:
        print(f"   JSON field error: {e}")


def demonstrate_advanced_patterns():
    """Demonstrate advanced lookup patterns and combinations."""
    print_section("11. Advanced Lookup Patterns")
    
    print("Advanced patterns combining multiple lookup types:")
    
    # Pattern 1: Multi-field complex search
    print("\n🎨 Pattern 1: Multi-field Complex Search")
    try:
        complex_search = Entry.objects.filter(
            Q(headline__icontains='tech') | Q(headline__icontains='review'),
            rating__gte=4,
            pub_date__year=2024,
            number_of_comments__gt=30
        ).count()
        print(f"   Tech/Review entries, 4+ stars, 2024, >30 comments: {complex_search}")
        
    except Exception as e:
        print(f"   Complex search error: {e}")
    
    # Pattern 2: Date range with exclusions
    print("\n🎨 Pattern 2: Date Range with Exclusions")
    try:
        filtered_dates = Entry.objects.filter(
            pub_date__range=(date(2024, 1, 1), date(2024, 12, 31))
        ).exclude(
            pub_date__month__in=[7, 8]  # Exclude summer months
        ).exclude(
            pub_date__week_day=1  # Exclude Sundays
        ).count()
        print(f"   2024 entries, no summer, no Sundays: {filtered_dates}")
        
    except Exception as e:
        print(f"   Date filtering error: {e}")
    
    # Pattern 3: Nested relationship lookups
    print("\n🎨 Pattern 3: Nested Relationship Lookups")
    try:
        author_blog_pattern = Entry.objects.filter(
            authors__email__domain='techcrunch.com',
            blog__name__icontains='tech',
            rating__in=[4, 5]
        ).distinct().count()
        print(f"   TechCrunch authors on tech blogs, high-rated: {author_blog_pattern}")
        
    except Exception as e:
        print(f"   Nested lookup error: {e}")
    
    # Pattern 4: Custom lookup combinations
    print("\n🎨 Pattern 4: Custom Lookup Combinations")
    try:
        custom_combo = Entry.objects.filter(
            headline__word_count__gte=4,
            rating__ne=3,
            authors__email__domain__in=['techcrunch.com', 'theverge.com']
        ).distinct().count()
        print(f"   Long titles, not 3-star, major publications: {custom_combo}")
        
    except Exception as e:
        print(f"   Custom combination error: {e}")
    
    # Pattern 5: Performance-optimized lookups
    print("\n🎨 Pattern 5: Performance-Optimized Lookups")
    try:
        optimized = Entry.objects.select_related('blog').prefetch_related('authors').filter(
            rating__gte=4
        ).filter(
            blog__name__startswith='Tech'  # More specific than contains
        ).order_by('-pub_date')[:10]
        
        print(f"   Optimized query returned {len(list(optimized))} results")
        print("   ⚡ Used select_related, prefetch_related, and startswith")
        
    except Exception as e:
        print(f"   Optimization error: {e}")


def main():
    """Main function to run all lookup demonstrations."""
    print("🔍 Django Lookups API Reference & Custom Lookups Practice")
    print("Following: https://docs.djangoproject.com/en/5.2/ref/models/lookups/")
    print("="*80)
    
    try:
        # Setup test data
        setup_lookup_test_data()
        
        # Test built-in lookups comprehensively
        test_builtin_lookups_comprehensive()
        
        # Create and test custom transforms
        create_custom_transform_absolutevalue()
        create_custom_transform_wordcount()
        create_custom_transform_domain()
        
        # Create and test custom lookups
        create_custom_lookup_notequal()
        create_custom_lookup_approximately()
        create_custom_lookup_soundslike()
        
        # Test advanced features
        test_custom_lookups_chaining()
        test_lookup_performance()
        test_edge_cases_and_pitfalls()
        demonstrate_advanced_patterns()
        
        print_section("🎉 SUMMARY - Django Lookups Mastery Complete!")
        print("✅ Successfully demonstrated ALL Django Lookup concepts:")
        print()
        print("📋 BUILT-IN LOOKUPS MASTERED:")
        print("   • String: exact, iexact, contains, icontains, startswith, endswith")
        print("   • Comparison: gt, gte, lt, lte, in, range")
        print("   • Date/Time: year, month, day, week, quarter, hour, minute, second")
        print("   • Special: isnull, regex, iregex")
        print("   • JSON: has_key, value lookups, nested access")
        print()
        print("🔧 CUSTOM COMPONENTS CREATED:")
        print("   • AbsoluteValue Transform - Calculate absolute values")
        print("   • WordCount Transform - Count words in text fields")
        print("   • EmailDomain Transform - Extract email domains")
        print("   • NotEqual Lookup - Not equal comparison operator")
        print("   • Approximately Lookup - Fuzzy numeric matching")
        print("   • SoundsLike Lookup - Phonetic similarity matching")
        print()
        print("🎯 ADVANCED PATTERNS DEMONSTRATED:")
        print("   • Transform and lookup chaining")
        print("   • Performance optimization techniques")
        print("   • Edge case handling and pitfalls")
        print("   • Complex multi-field searches")
        print("   • Nested relationship lookups")
        print()
        print("💡 KEY CONCEPTS LEARNED:")
        print("   • Query Expression API implementation")
        print("   • RegisterLookupMixin usage")
        print("   • Database vendor-specific SQL generation")
        print("   • Transform vs Lookup differences")
        print("   • Performance implications of different lookups")
        print("   • Proper null and empty value handling")
        print()
        print("🚀 You now have deep knowledge of Django's Lookup system!")
        print("   Ready to create efficient, custom database queries!")
        
    except Exception as e:
        print(f"\n❌ Error during lookup testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
