#!/usr/bin/env python
"""
Django QuerySet API Interactive Practice Guide
Following https://docs.djangoproject.com/en/5.2/ref/models/querysets/

Interactive exercises to master ALL Django QuerySet methods and operations.
This guide provides hands-on practice with real examples and explanations.
"""

import os
import sys
import django

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modelspractice.settings')
    django.setup()

from django.db import models
from django.db.models import (
    Q, F, Count, Sum, Avg, Max, Min, StdDev, Variance, 
    Case, When, Value, Prefetch, FilteredRelation
)
from django.db.models.functions import Lower, Upper, Extract, Coalesce, Length
from datetime import date, datetime, timedelta
from decimal import Decimal
from query_practice.models import *


class QuerySetPracticeGuide:
    """Interactive guide for Django QuerySet API practice."""
    
    def __init__(self):
        self.section_number = 0
        self.exercise_number = 0
        
    def print_header(self, title, level=1):
        """Print formatted headers."""
        if level == 1:
            self.section_number += 1
            self.exercise_number = 0
            print(f"\n{'='*80}")
            print(f"SECTION {self.section_number}: {title}")
            print(f"{'='*80}")
        elif level == 2:
            self.exercise_number += 1
            print(f"\n{'-'*60}")
            print(f"Exercise {self.section_number}.{self.exercise_number}: {title}")
            print(f"{'-'*60}")
        else:
            print(f"\n### {title} ###")
    
    def print_task(self, task):
        """Print exercise task."""
        print(f"\n🎯 TASK: {task}")
    
    def print_hint(self, hint):
        """Print hint for exercise."""
        print(f"\n💡 HINT: {hint}")
    
    def print_solution(self, solution, explanation=""):
        """Print solution with explanation."""
        print(f"\n✅ SOLUTION:")
        print(f"   {solution}")
        if explanation:
            print(f"\n📝 EXPLANATION: {explanation}")
    
    def print_result(self, result, title="RESULT"):
        """Print formatted result."""
        print(f"\n📊 {title}: {result}")
    
    def wait_for_user(self):
        """Wait for user input to continue."""
        input("\n⏸️  Press Enter to see solution...")
    
    def demonstrate_method(self, method_name, description, code, result=None):
        """Demonstrate a QuerySet method."""
        print(f"\n🔧 {method_name}: {description}")
        print(f"   Code: {code}")
        if result is not None:
            print(f"   Result: {result}")


def section_1_queryset_evaluation(guide):
    """Section 1: Understanding QuerySet Evaluation"""
    guide.print_header("Understanding QuerySet Evaluation")
    
    print("""
📚 THEORY: QuerySets are LAZY - they don't hit the database until evaluated.
Understanding when evaluation occurs is crucial for performance optimization.

EVALUATION TRIGGERS:
• Iteration (for item in queryset)
• Slicing with step ([::2])
• repr() or str()
• len()
• list()
• bool()
• Pickling
""")
    
    guide.print_header("Testing QuerySet Evaluation", 2)
    guide.print_task("Create a QuerySet and test different evaluation triggers")
    guide.print_hint("Use Entry.objects.filter() and test iteration, len(), bool(), etc.")
    guide.wait_for_user()
    
    # Demonstrate evaluation
    print("\n1. Creating QuerySet (no DB hit):")
    qs = Entry.objects.filter(rating__gte=4)
    print(f"   Type: {type(qs)}")
    print(f"   _result_cache: {getattr(qs, '_result_cache', 'Not cached')}")
    
    print("\n2. Testing len() - hits database:")
    length = len(qs)
    print(f"   Length: {length}")
    print(f"   _result_cache: {getattr(qs, '_result_cache', 'Not cached')}")
    
    print("\n3. Testing iteration - uses cache:")
    count = 0
    for entry in qs:
        count += 1
        if count <= 3:
            print(f"   Entry: {entry.headline}")
        if count >= 3:
            break
    
    print("\n4. Slicing without step - returns new QuerySet:")
    sliced = Entry.objects.all()[:5]
    print(f"   Type: {type(sliced)}")
    
    print("\n5. Slicing with step - evaluates QuerySet:")
    stepped = Entry.objects.all()[::2]
    print(f"   Type: {type(stepped)}")


def section_2_methods_returning_querysets(guide):
    """Section 2: Methods that Return New QuerySets"""
    guide.print_header("Methods that Return New QuerySets")
    
    print("""
🔄 These methods return new QuerySet objects, allowing for method chaining.
They are lazy and don't execute until the QuerySet is evaluated.
""")
    
    guide.print_header("filter() and exclude()", 2)
    guide.print_task("Find all high-rated entries from tech blogs, excluding test entries")
    guide.print_hint("Chain filter() methods and use exclude() with icontains lookup")
    guide.wait_for_user()
    
    result = Entry.objects.filter(
        rating__gte=4
    ).filter(
        blog__name__icontains='tech'
    ).exclude(
        headline__icontains='test'
    )
    guide.print_solution(
        "Entry.objects.filter(rating__gte=4).filter(blog__name__icontains='tech').exclude(headline__icontains='test')",
        "Chain multiple filters and use exclude to remove unwanted results"
    )
    guide.print_result(f"{result.count()} entries found")
    
    guide.print_header("annotate() with calculations", 2)
    guide.print_task("Add calculated fields: engagement score, popularity status, author count")
    guide.print_hint("Use F expressions for calculations, Case/When for conditions, Count for relationships")
    guide.wait_for_user()
    
    annotated = Entry.objects.annotate(
        engagement_score=F('number_of_comments') + F('number_of_pingbacks'),
        is_popular=Case(
            When(rating__gte=4, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField()
        ),
        author_count=Count('authors')
    ).filter(engagement_score__gt=10)[:5]
    
    guide.print_solution("""
Entry.objects.annotate(
    engagement_score=F('number_of_comments') + F('number_of_pingbacks'),
    is_popular=Case(When(rating__gte=4, then=Value(True)), default=Value(False)),
    author_count=Count('authors')
).filter(engagement_score__gt=10)[:5]""",
        "Annotate adds calculated fields that can be used in filtering and ordering"
    )
    
    for entry in annotated:
        print(f"   {entry.headline}: engagement={entry.engagement_score}, popular={entry.is_popular}")
    
    guide.print_header("order_by() with expressions", 2)
    guide.print_task("Order entries by rating (5-star first), then by engagement score descending")
    guide.print_hint("Use Case expression to prioritize 5-star ratings, then F expressions")
    guide.wait_for_user()
    
    ordered = Entry.objects.annotate(
        engagement=F('number_of_comments') + F('number_of_pingbacks')
    ).order_by(
        Case(When(rating=5, then=1), default=2),
        '-engagement'
    )[:5]
    
    guide.print_solution("""
Entry.objects.annotate(engagement=F('number_of_comments') + F('number_of_pingbacks'))
.order_by(Case(When(rating=5, then=1), default=2), '-engagement')""",
        "Use Case expression to create custom ordering logic"
    )
    
    for entry in ordered:
        print(f"   {entry.headline}: rating={entry.rating}, engagement={entry.engagement}")
    
    guide.print_header("values() and values_list()", 2)
    guide.print_task("Get entry data as dictionaries and tuples with calculated fields")
    guide.print_hint("Use values() for dictionaries, values_list() for tuples, add calculated fields")
    guide.wait_for_user()
    
    # Values as dictionaries
    values_dict = Entry.objects.annotate(
        blog_name=F('blog__name'),
        engagement=F('number_of_comments') + F('number_of_pingbacks')
    ).values('headline', 'rating', 'blog_name', 'engagement')[:3]
    
    # Values as tuples
    values_tuple = Entry.objects.values_list('headline', 'rating', 'blog__name')[:3]
    
    # Flat values
    ratings = Entry.objects.values_list('rating', flat=True).distinct().order_by('rating')
    
    guide.print_solution("""
# Dictionaries with annotations:
Entry.objects.annotate(blog_name=F('blog__name')).values('headline', 'rating', 'blog_name')

# Tuples:
Entry.objects.values_list('headline', 'rating', 'blog__name')

# Flat list:
Entry.objects.values_list('rating', flat=True).distinct()""",
        "values() returns dicts, values_list() returns tuples, flat=True returns single values"
    )
    
    print("   Dictionary format:")
    for item in values_dict:
        print(f"      {item}")
    
    print(f"\n   Unique ratings: {list(ratings)}")


def section_3_optimization_methods(guide):
    """Section 3: Query Optimization Methods"""
    guide.print_header("Query Optimization Methods")
    
    print("""
⚡ Performance optimization is crucial for Django applications.
Learn select_related, prefetch_related, only, defer for efficient queries.
""")
    
    guide.print_header("select_related() for ForeignKey optimization", 2)
    guide.print_task("Get entries with blog names efficiently (avoid N+1 queries)")
    guide.print_hint("Use select_related() for ForeignKey relationships like blog")
    guide.wait_for_user()
    
    # Demonstrate N+1 problem
    print("❌ BAD: Without select_related (N+1 queries):")
    entries_bad = Entry.objects.all()[:3]
    for entry in entries_bad:
        print(f"   {entry.headline} in {entry.blog.name}")  # Each access hits DB
    
    # Optimized version
    print("\n✅ GOOD: With select_related (single query):")
    entries_good = Entry.objects.select_related('blog')[:3]
    for entry in entries_good:
        print(f"   {entry.headline} in {entry.blog.name}")  # No additional queries
    
    guide.print_solution(
        "Entry.objects.select_related('blog')",
        "select_related performs SQL JOIN to fetch related objects in one query"
    )
    
    guide.print_header("prefetch_related() for ManyToMany optimization", 2)
    guide.print_task("Get entries with all their authors efficiently")
    guide.print_hint("Use prefetch_related() for ManyToMany and reverse ForeignKey relationships")
    guide.wait_for_user()
    
    entries_with_authors = Entry.objects.prefetch_related('authors')[:3]
    
    guide.print_solution(
        "Entry.objects.prefetch_related('authors')",
        "prefetch_related performs separate queries then joins in Python"
    )
    
    for entry in entries_with_authors:
        authors = [author.name for author in entry.authors.all()]
        print(f"   {entry.headline} by: {', '.join(authors) or 'No authors'}")
    
    guide.print_header("Custom Prefetch objects", 2)
    guide.print_task("Get blogs with only their high-rated entries")
    guide.print_hint("Use Prefetch object with custom queryset and to_attr")
    guide.wait_for_user()
    
    high_rated_prefetch = Prefetch(
        'entry_set',
        queryset=Entry.objects.filter(rating__gte=4).order_by('-rating'),
        to_attr='high_rated_entries'
    )
    
    blogs_with_high_rated = Blog.objects.prefetch_related(high_rated_prefetch)[:3]
    
    guide.print_solution("""
Prefetch('entry_set', 
    queryset=Entry.objects.filter(rating__gte=4).order_by('-rating'),
    to_attr='high_rated_entries')""",
        "Custom Prefetch allows filtering and custom attribute names"
    )
    
    for blog in blogs_with_high_rated:
        high_rated = getattr(blog, 'high_rated_entries', [])
        print(f"   {blog.name}: {len(high_rated)} high-rated entries")
    
    guide.print_header("only() and defer() for field selection", 2)
    guide.print_task("Load entries with only essential fields, defer large body_text")
    guide.print_hint("Use only() for specific fields, defer() to exclude fields")
    guide.wait_for_user()
    
    # Only specific fields
    essential_only = Entry.objects.only('headline', 'rating', 'pub_date')[:3]
    
    # Defer large fields
    without_body = Entry.objects.defer('body_text')[:3]
    
    guide.print_solution("""
# Load only specific fields:
Entry.objects.only('headline', 'rating', 'pub_date')

# Exclude specific fields:
Entry.objects.defer('body_text')""",
        "only() loads specific fields, defer() excludes fields until accessed"
    )
    
    print("   Only essential fields:")
    for entry in essential_only:
        print(f"      {entry.headline}: {entry.rating} ({entry.pub_date})")


def section_4_aggregation_and_grouping(guide):
    """Section 4: Aggregation and Grouping"""
    guide.print_header("Aggregation and Grouping")
    
    print("""
📊 Aggregation allows you to perform calculations across multiple rows.
Master Count, Sum, Avg, Max, Min, StdDev, Variance with grouping.
""")
    
    guide.print_header("Basic aggregations", 2)
    guide.print_task("Calculate comprehensive statistics for all entries")
    guide.print_hint("Use aggregate() with Count, Avg, Max, Min, Sum, StdDev")
    guide.wait_for_user()
    
    stats = Entry.objects.aggregate(
        total_entries=Count('id'),
        avg_rating=Avg('rating'),
        max_rating=Max('rating'),
        min_rating=Min('rating'),
        total_comments=Sum('number_of_comments'),
        rating_std=StdDev('rating'),
        rating_var=Variance('rating')
    )
    
    guide.print_solution("""
Entry.objects.aggregate(
    total_entries=Count('id'),
    avg_rating=Avg('rating'),
    max_rating=Max('rating'),
    min_rating=Min('rating'),
    total_comments=Sum('number_of_comments'),
    rating_std=StdDev('rating'),
    rating_var=Variance('rating')
)""", "aggregate() performs calculations across all matching rows")
    
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    guide.print_header("Grouping with annotations", 2)
    guide.print_task("Get statistics for each blog: entry count, average rating, total comments")
    guide.print_hint("Use annotate() to group by blog and calculate stats per group")
    guide.wait_for_user()
    
    blog_stats = Blog.objects.annotate(
        entry_count=Count('entry'),
        avg_rating=Avg('entry__rating'),
        max_rating=Max('entry__rating'),
        total_comments=Sum('entry__number_of_comments'),
        recent_entries=Count('entry', filter=Q(entry__pub_date__gte=date(2024, 6, 1)))
    ).values('name', 'entry_count', 'avg_rating', 'max_rating', 'total_comments', 'recent_entries')
    
    guide.print_solution("""
Blog.objects.annotate(
    entry_count=Count('entry'),
    avg_rating=Avg('entry__rating'),
    total_comments=Sum('entry__number_of_comments'),
    recent_entries=Count('entry', filter=Q(entry__pub_date__gte=date(2024, 6, 1)))
)""", "annotate() with aggregations groups by the model's primary key")
    
    for blog in blog_stats:
        avg_rating = blog['avg_rating']
        avg_str = f"{avg_rating:.2f}" if avg_rating else "N/A"
        print(f"   {blog['name']}: {blog['entry_count']} entries, avg rating: {avg_str}")
        print(f"      Total comments: {blog['total_comments'] or 0}, Recent: {blog['recent_entries']}")
    
    guide.print_header("Conditional aggregations", 2)
    guide.print_task("Count high-rated vs low-rated entries per blog")
    guide.print_hint("Use Count with filter parameter and Q objects")
    guide.wait_for_user()
    
    conditional_stats = Blog.objects.annotate(
        total_entries=Count('entry'),
        high_rated=Count('entry', filter=Q(entry__rating__gte=4)),
        low_rated=Count('entry', filter=Q(entry__rating__lt=3)),
        avg_high_rated=Avg('entry__rating', filter=Q(entry__rating__gte=4))
    ).values('name', 'total_entries', 'high_rated', 'low_rated', 'avg_high_rated')
    
    guide.print_solution("""
Blog.objects.annotate(
    high_rated=Count('entry', filter=Q(entry__rating__gte=4)),
    low_rated=Count('entry', filter=Q(entry__rating__lt=3)),
    avg_high_rated=Avg('entry__rating', filter=Q(entry__rating__gte=4))
)""", "filter parameter in aggregations allows conditional calculations")
    
    for blog in conditional_stats:
        print(f"   {blog['name']}: {blog['total_entries']} total")
        print(f"      High-rated: {blog['high_rated']}, Low-rated: {blog['low_rated']}")


def section_5_complex_queries(guide):
    """Section 5: Complex Queries with Q and F objects"""
    guide.print_header("Complex Queries with Q and F Objects")
    
    print("""
🔧 Q objects enable complex logical operations (AND, OR, NOT, XOR).
F objects reference model fields for comparisons and calculations.
""")
    
    guide.print_header("Q object combinations", 2)
    guide.print_task("Find entries that are either high-rated OR from tech blogs, but NOT test entries")
    guide.print_hint("Use Q objects with |, &, and ~ operators")
    guide.wait_for_user()
    
    q_high_rated = Q(rating__gte=4)
    q_tech_blog = Q(blog__name__icontains='tech')
    q_not_test = ~Q(headline__icontains='test')
    
    complex_query = (q_high_rated | q_tech_blog) & q_not_test
    results = Entry.objects.filter(complex_query).count()
    
    guide.print_solution("""
q_high_rated = Q(rating__gte=4)
q_tech_blog = Q(blog__name__icontains='tech') 
q_not_test = ~Q(headline__icontains='test')
complex_query = (q_high_rated | q_tech_blog) & q_not_test""",
        "Q objects support logical operators: & (AND), | (OR), ~ (NOT), ^ (XOR)"
    )
    guide.print_result(f"{results} entries match the complex criteria")
    
    guide.print_header("F expressions for field comparisons", 2)
    guide.print_task("Find entries where comments exceed pingbacks by more than 10")
    guide.print_hint("Use F expressions to reference and compare fields")
    guide.wait_for_user()
    
    f_comparison = Entry.objects.filter(
        number_of_comments__gt=F('number_of_pingbacks') + 10
    ).annotate(
        comment_advantage=F('number_of_comments') - F('number_of_pingbacks')
    )[:5]
    
    guide.print_solution("""
Entry.objects.filter(
    number_of_comments__gt=F('number_of_pingbacks') + 10
).annotate(
    comment_advantage=F('number_of_comments') - F('number_of_pingbacks')
)""", "F expressions reference model fields and support arithmetic operations")
    
    for entry in f_comparison:
        print(f"   {entry.headline}: +{entry.comment_advantage} comment advantage")
    
    guide.print_header("Advanced Q and F combinations", 2)
    guide.print_task("Find profitable products with high stock, considering price-cost ratio")
    guide.print_hint("Combine Q objects with F expressions for complex business logic")
    guide.wait_for_user()
    
    profitable_products = Product.objects.filter(
        Q(price__gt=F('cost') * Decimal('1.5')) &  # >50% profit margin
        Q(stock_quantity__gte=20) &  # High stock
        (Q(name__icontains='pro') | Q(specifications__color='Black'))  # Premium or black
    ).annotate(
        profit_amount=F('price') - F('cost'),
        profit_margin=((F('price') - F('cost')) / F('price')) * 100
    )
    
    guide.print_solution("""
Product.objects.filter(
    Q(price__gt=F('cost') * Decimal('1.5')) &
    Q(stock_quantity__gte=20) &
    (Q(name__icontains='pro') | Q(specifications__color='Black'))
).annotate(
    profit_amount=F('price') - F('cost'),
    profit_margin=((F('price') - F('cost')) / F('price')) * 100
)""", "Complex business logic combining Q objects, F expressions, and annotations")
    
    for product in profitable_products:
        print(f"   {product.name}: ${product.profit_amount:.2f} profit ({product.profit_margin:.1f}%)")


def section_6_field_lookups_mastery(guide):
    """Section 6: Master All Field Lookups"""
    guide.print_header("Master All Field Lookups")
    
    print("""
🔍 Django provides 30+ field lookup types for precise querying.
Master exact, contains, comparisons, date/time, and special lookups.
""")
    
    guide.print_header("String lookups", 2)
    guide.print_task("Practice all string-based lookups with case sensitivity")
    guide.print_hint("Use exact, iexact, contains, icontains, startswith, endswith variants")
    guide.wait_for_user()
    
    string_lookups = {
        'exact': Entry.objects.filter(blog__name__exact='Tech Innovations').count(),
        'iexact': Entry.objects.filter(blog__name__iexact='TECH INNOVATIONS').count(),
        'contains': Entry.objects.filter(headline__contains='Tech').count(),
        'icontains': Entry.objects.filter(headline__icontains='TECH').count(),
        'startswith': Entry.objects.filter(headline__startswith='Entry').count(),
        'istartswith': Entry.objects.filter(headline__istartswith='ENTRY').count(),
        'endswith': Entry.objects.filter(headline__endswith='Article').count(),
        'iendswith': Entry.objects.filter(headline__iendswith='ARTICLE').count(),
    }
    
    guide.print_solution("""
# Case-sensitive vs case-insensitive lookups:
Entry.objects.filter(blog__name__exact='Tech Innovations')  # Exact match
Entry.objects.filter(blog__name__iexact='TECH INNOVATIONS')  # Case-insensitive
Entry.objects.filter(headline__contains='Tech')  # Contains substring
Entry.objects.filter(headline__icontains='TECH')  # Case-insensitive contains""",
        "i-prefixed lookups are case-insensitive versions"
    )
    
    for lookup, count in string_lookups.items():
        print(f"   {lookup}: {count} matches")
    
    guide.print_header("Date and time lookups", 2)
    guide.print_task("Query entries by various date/time components")
    guide.print_hint("Use year, month, day, week, hour, minute, second lookups")
    guide.wait_for_user()
    
    date_lookups = {
        'year 2024': Entry.objects.filter(pub_date__year=2024).count(),
        'month >= 6': Entry.objects.filter(pub_date__month__gte=6).count(),
        'day 15': Entry.objects.filter(pub_date__day=15).count(),
        'week 25': Entry.objects.filter(pub_date__week=25).count(),
        'weekday Monday': Entry.objects.filter(pub_date__week_day=2).count(),
        'quarter Q2': Entry.objects.filter(pub_date__quarter=2).count(),
    }
    
    guide.print_solution("""
# Date component lookups:
Entry.objects.filter(pub_date__year=2024)
Entry.objects.filter(pub_date__month__gte=6)
Entry.objects.filter(pub_date__day=15)
Entry.objects.filter(pub_date__week=25)
Entry.objects.filter(pub_date__week_day=2)  # Sunday=1, Monday=2, etc.
Entry.objects.filter(pub_date__quarter=2)""",
        "Date lookups extract specific components for filtering"
    )
    
    for lookup, count in date_lookups.items():
        print(f"   {lookup}: {count} matches")
    
    guide.print_header("Range and list lookups", 2)
    guide.print_task("Find entries using range and list-based filtering")
    guide.print_hint("Use range, in, and comparison operators")
    guide.wait_for_user()
    
    # Range and list operations
    range_results = Entry.objects.filter(
        rating__range=(3, 5),  # Between 3 and 5 inclusive
        number_of_comments__in=[0, 5, 10, 15, 20],  # Specific values
        pub_date__range=(date(2024, 1, 1), date(2024, 6, 30))  # Date range
    ).count()
    
    guide.print_solution("""
Entry.objects.filter(
    rating__range=(3, 5),  # Between 3 and 5 inclusive
    number_of_comments__in=[0, 5, 10, 15, 20],  # Specific values  
    pub_date__range=(date(2024, 1, 1), date(2024, 6, 30))  # Date range
)""", "range uses BETWEEN, in uses IN, both are inclusive")
    
    guide.print_result(f"{range_results} entries in specified ranges")


def section_7_advanced_features(guide):
    """Section 7: Advanced Features"""
    guide.print_header("Advanced Features")
    
    print("""
🚀 Advanced Django QuerySet features for complex applications:
JSON fields, window functions, raw SQL, and performance monitoring.
""")
    
    guide.print_header("JSON field operations", 2)
    guide.print_task("Query products by JSON specifications")
    guide.print_hint("Use JSON key lookups, has_key, and value filtering")
    guide.wait_for_user()
    
    # JSON field queries
    json_queries = {
        'has color': Product.objects.filter(specifications__has_key='color').count(),
        'black products': Product.objects.filter(specifications__color='Black').count(),
        'warranty info': Product.objects.filter(specifications__warranty__isnull=False).count(),
    }
    
    # Get products with specific JSON values
    json_products = Product.objects.filter(
        specifications__color='Black'
    ).values('name', 'specifications__color', 'specifications__warranty')[:3]
    
    guide.print_solution("""
# JSON field lookups:
Product.objects.filter(specifications__has_key='color')  # Has key
Product.objects.filter(specifications__color='Black')    # Key value
Product.objects.filter(specifications__warranty__isnull=False)  # Not null""",
        "JSON fields support key lookups and value filtering"
    )
    
    for key, count in json_queries.items():
        print(f"   {key}: {count} products")
    
    print("\n   Product specifications:")
    for product in json_products:
        print(f"      {product['name']}: {product['specifications__color']}")
    
    guide.print_header("Raw SQL when needed", 2)
    guide.print_task("Use raw SQL for complex database-specific operations")
    guide.print_hint("Use raw() method for custom SQL while maintaining model instances")
    guide.wait_for_user()
    
    # Raw SQL example
    raw_entries = Entry.objects.raw("""
        SELECT * FROM query_practice_entry 
        WHERE rating >= %s 
        AND number_of_comments > number_of_pingbacks * 2
        ORDER BY pub_date DESC
    """, [4])
    
    guide.print_solution("""
Entry.objects.raw('''
    SELECT * FROM query_practice_entry 
    WHERE rating >= %s 
    AND number_of_comments > number_of_pingbacks * 2
    ORDER BY pub_date DESC
''', [4])""", "raw() executes custom SQL but returns model instances")
    
    raw_list = list(raw_entries)[:3]
    for entry in raw_list:
        print(f"   {entry.headline}: {entry.rating} stars")
    
    guide.print_header("Performance monitoring", 2)
    guide.print_task("Monitor and explain query performance")
    guide.print_hint("Use explain() method and QuerySet caching behavior")
    guide.wait_for_user()
    
    # Query explanation
    complex_query = Entry.objects.select_related('blog').filter(
        rating__gte=4
    ).order_by('-pub_date')
    
    try:
        explanation = complex_query.explain()
        print("   Query execution plan:")
        print(f"   {explanation[:200]}..." if len(explanation) > 200 else explanation)
    except Exception as e:
        print(f"   Query explanation not available: {e}")
    
    # Demonstrate caching
    print("\n   QuerySet caching behavior:")
    qs = Entry.objects.filter(rating=5)
    print(f"   Created QuerySet, cached: {hasattr(qs, '_result_cache')}")
    
    # First access
    count1 = len(list(qs))
    print(f"   After first evaluation, cached: {hasattr(qs, '_result_cache')}")
    
    # Second access uses cache
    count2 = len(list(qs))
    print(f"   Second access uses cache: {count1 == count2}")


def main():
    """Main interactive practice session."""
    guide = QuerySetPracticeGuide()
    
    print("🎓 Django QuerySet API Interactive Practice Guide")
    print("Following: https://docs.djangoproject.com/en/5.2/ref/models/querysets/")
    print("="*80)
    print("""
🎯 LEARNING OBJECTIVES:
• Master all QuerySet evaluation triggers and caching behavior
• Use all 40+ QuerySet methods effectively
• Apply complex filtering with Q and F objects
• Optimize queries with select_related and prefetch_related
• Perform advanced aggregations and grouping
• Handle all 30+ field lookup types
• Implement complex business logic with Django ORM

📋 PRACTICE SECTIONS:
1. QuerySet Evaluation - Understanding lazy evaluation
2. Methods Returning QuerySets - Chaining and filtering
3. Query Optimization - Performance best practices
4. Aggregation and Grouping - Statistical calculations
5. Complex Queries - Q objects and F expressions
6. Field Lookups Mastery - All lookup types
7. Advanced Features - JSON, raw SQL, monitoring

💡 TIPS:
• Try each exercise yourself before viewing the solution
• Experiment with variations and combinations
• Use Django shell to test queries interactively
• Monitor query performance with explain()
""")
    
    choice = input("\n🚀 Ready to start? (y/n): ").lower()
    if choice != 'y':
        print("Come back when you're ready to master Django QuerySets! 📚")
        return
    
    try:
        # Run all practice sections
        section_1_queryset_evaluation(guide)
        section_2_methods_returning_querysets(guide)
        section_3_optimization_methods(guide)
        section_4_aggregation_and_grouping(guide)
        section_5_complex_queries(guide)
        section_6_field_lookups_mastery(guide)
        section_7_advanced_features(guide)
        
        print("\n" + "="*80)
        print("🎉 CONGRATULATIONS! QuerySet API Mastery Complete!")
        print("="*80)
        print("""
✅ YOU HAVE MASTERED:
• QuerySet evaluation and caching mechanisms
• All 40+ QuerySet methods and their use cases
• Query optimization techniques for performance
• Complex filtering and logical operations
• Advanced aggregation and statistical calculations
• Complete field lookup reference (30+ types)
• Advanced features like JSON fields and raw SQL

🚀 NEXT STEPS:
• Practice with your own models and data
• Combine techniques for complex business logic
• Monitor and optimize query performance
• Explore Django's advanced ORM features
• Build efficient, scalable Django applications

🎓 You're now ready to handle any Django database query challenge!
""")
        
    except KeyboardInterrupt:
        print("\n\n⏸️  Practice session interrupted. Resume anytime!")
    except Exception as e:
        print(f"\n❌ Error during practice: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
