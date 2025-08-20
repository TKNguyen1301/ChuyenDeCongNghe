#!/usr/bin/env python
"""
Django Lookups Interactive Practice Guide
Following https://docs.djangoproject.com/en/5.2/ref/models/lookups/

Interactive exercises to master Django Lookups API, custom transforms, and lookups.
This guide provides hands-on practice with real-world examples.
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
    Q, F, Count, Sum, Avg, Transform, Lookup, Field, 
    IntegerField, CharField, FloatField, Value
)
from datetime import date, datetime, timedelta
from decimal import Decimal
from query_practice.models import *


class LookupsPracticeGuide:
    """Interactive guide for Django Lookups practice."""
    
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
        if isinstance(solution, list):
            for line in solution:
                print(f"   {line}")
        else:
            print(f"   {solution}")
        if explanation:
            print(f"\n📝 EXPLANATION: {explanation}")
    
    def print_result(self, result, title="RESULT"):
        """Print formatted result."""
        print(f"\n📊 {title}: {result}")
    
    def wait_for_user(self):
        """Wait for user input to continue."""
        input("\n⏸️  Press Enter to see solution...")
    
    def show_lookup_structure(self, lookup_example):
        """Show the structure of a lookup."""
        print(f"\n🔍 LOOKUP STRUCTURE: {lookup_example}")
        parts = lookup_example.split('__')
        if len(parts) >= 2:
            print(f"   Field: {parts[0]}")
            if len(parts) > 2:
                print(f"   Transforms: {' → '.join(parts[1:-1])}")
            print(f"   Lookup: {parts[-1]}")


def section_1_builtin_lookups_mastery(guide):
    """Section 1: Master All Built-in Lookups"""
    guide.print_header("Master All Built-in Lookups")
    
    print("""
📚 THEORY: Django provides 30+ built-in lookups for different data types.
Understanding when and how to use each lookup is crucial for efficient queries.

LOOKUP CATEGORIES:
• String: exact, iexact, contains, icontains, startswith, endswith
• Numeric: gt, gte, lt, lte, in, range
• Date/Time: year, month, day, week, quarter, hour, minute, second
• Special: isnull, regex, iregex
• JSON: has_key, value access, nested paths
""")
    
    guide.print_header("String Lookups Practice", 2)
    guide.print_task("Find entries with headlines containing 'Tech' (case-sensitive and insensitive)")
    guide.print_hint("Use contains and icontains lookups, compare the results")
    guide.wait_for_user()
    
    # Demonstrate string lookups
    contains_tech = Entry.objects.filter(headline__contains='Tech').count()
    icontains_tech = Entry.objects.filter(headline__icontains='TECH').count()
    startswith_tech = Entry.objects.filter(headline__startswith='Tech').count()
    endswith_review = Entry.objects.filter(headline__endswith='Review').count()
    
    guide.print_solution([
        "# Case-sensitive search:",
        "Entry.objects.filter(headline__contains='Tech')",
        "",
        "# Case-insensitive search:",
        "Entry.objects.filter(headline__icontains='TECH')",
        "",
        "# Position-specific searches:",
        "Entry.objects.filter(headline__startswith='Tech')",
        "Entry.objects.filter(headline__endswith='Review')"
    ], "String lookups are fundamental for text searching. 'i' prefix makes them case-insensitive.")
    
    print(f"   contains 'Tech': {contains_tech}")
    print(f"   icontains 'TECH': {icontains_tech}")
    print(f"   startswith 'Tech': {startswith_tech}")
    print(f"   endswith 'Review': {endswith_review}")
    
    guide.print_header("Numeric Comparison Lookups", 2)
    guide.print_task("Find high-quality content: entries with rating > 4 AND comments >= 30")
    guide.print_hint("Combine gt and gte lookups with filter chaining")
    guide.wait_for_user()
    
    high_quality = Entry.objects.filter(
        rating__gt=4,
        number_of_comments__gte=30
    )
    
    # Also show range alternative
    rating_range = Entry.objects.filter(rating__range=(4, 5))
    
    guide.print_solution([
        "# Multiple comparisons:",
        "Entry.objects.filter(rating__gt=4, number_of_comments__gte=30)",
        "",
        "# Alternative with range:",
        "Entry.objects.filter(rating__range=(4, 5))",
        "",
        "# Available comparisons: gt, gte, lt, lte, in, range"
    ], "Comparison lookups are essential for filtering numeric data")
    
    print(f"   High quality entries: {high_quality.count()}")
    print(f"   Rating 4-5 range: {rating_range.count()}")
    
    guide.print_header("Date/Time Component Lookups", 2)
    guide.print_task("Find entries published in 2024, in January, on the 1st day of month")
    guide.print_hint("Use year, month, and day lookups on pub_date field")
    guide.wait_for_user()
    
    year_2024 = Entry.objects.filter(pub_date__year=2024).count()
    january = Entry.objects.filter(pub_date__month=1).count()
    first_day = Entry.objects.filter(pub_date__day=1).count()
    q1_2024 = Entry.objects.filter(
        pub_date__year=2024,
        pub_date__quarter=1
    ).count()
    
    guide.print_solution([
        "# Date component filtering:",
        "Entry.objects.filter(pub_date__year=2024)",
        "Entry.objects.filter(pub_date__month=1)",
        "Entry.objects.filter(pub_date__day=1)",
        "",
        "# Quarter filtering:",
        "Entry.objects.filter(pub_date__quarter=1)",
        "",
        "# Available: year, month, day, week, quarter, hour, minute, second"
    ], "Date component lookups extract specific parts of dates for filtering")
    
    print(f"   Published in 2024: {year_2024}")
    print(f"   Published in January: {january}")
    print(f"   Published on 1st: {first_day}")
    print(f"   Q1 2024: {q1_2024}")
    
    guide.print_header("List and Range Operations", 2)
    guide.print_task("Find entries with specific ratings [4, 5] and comments in range 20-50")
    guide.print_hint("Use 'in' lookup for lists and 'range' for continuous ranges")
    guide.wait_for_user()
    
    top_ratings = Entry.objects.filter(rating__in=[4, 5])
    comment_range = Entry.objects.filter(number_of_comments__range=(20, 50))
    combined = Entry.objects.filter(
        rating__in=[4, 5],
        number_of_comments__range=(20, 50)
    )
    
    guide.print_solution([
        "# List membership:",
        "Entry.objects.filter(rating__in=[4, 5])",
        "",
        "# Range (inclusive both ends):",
        "Entry.objects.filter(number_of_comments__range=(20, 50))",
        "",
        "# Combined conditions:",
        "Entry.objects.filter(rating__in=[4, 5], number_of_comments__range=(20, 50))"
    ], "'in' checks list membership, 'range' is inclusive on both ends")
    
    print(f"   Top ratings: {top_ratings.count()}")
    print(f"   Comment range 20-50: {comment_range.count()}")
    print(f"   Combined criteria: {combined.count()}")


def section_2_custom_transforms(guide):
    """Section 2: Creating Custom Transforms"""
    guide.print_header("Creating Custom Transforms")
    
    print("""
🔧 THEORY: Transforms modify field values before applying lookups.
They follow the Query Expression API and can be chained.

TRANSFORM COMPONENTS:
• lookup_name: The name used in queries (e.g., 'abs' for __abs)
• output_field: The field type returned by the transform
• as_sql(): Method that generates the SQL for the transformation
""")
    
    guide.print_header("Create Length Transform", 2)
    guide.print_task("Create a transform that calculates text length")
    guide.print_hint("Inherit from Transform, set lookup_name='length', use LENGTH() SQL function")
    guide.wait_for_user()
    
    # Create the transform
    class Length(Transform):
        lookup_name = 'length'
        function = 'LENGTH'
        
        @property
        def output_field(self):
            return IntegerField()
    
    # Register it
    CharField.register_lookup(Length)
    models.TextField.register_lookup(Length)
    
    guide.print_solution([
        "class Length(Transform):",
        "    lookup_name = 'length'",
        "    function = 'LENGTH'",
        "    ",
        "    @property",
        "    def output_field(self):",
        "        return IntegerField()",
        "",
        "# Register on text fields:",
        "CharField.register_lookup(Length)",
        "models.TextField.register_lookup(Length)"
    ], "Transforms modify field values. This one calculates string length.")
    
    # Test the transform
    try:
        long_headlines = Entry.objects.filter(headline__length__gt=20).count()
        short_headlines = Entry.objects.filter(headline__length__lte=15).count()
        print(f"   Headlines > 20 chars: {long_headlines}")
        print(f"   Headlines ≤ 15 chars: {short_headlines}")
    except Exception as e:
        print(f"   Transform test error: {e}")
    
    guide.print_header("Create Upper Transform", 2)
    guide.print_task("Create a transform that converts text to uppercase")
    guide.print_hint("Use UPPER() SQL function, output_field should be CharField")
    guide.wait_for_user()
    
    class Upper(Transform):
        lookup_name = 'upper'
        function = 'UPPER'
        
        @property
        def output_field(self):
            return CharField()
    
    CharField.register_lookup(Upper)
    models.TextField.register_lookup(Upper)
    
    guide.print_solution([
        "class Upper(Transform):",
        "    lookup_name = 'upper'",
        "    function = 'UPPER'",
        "    ",
        "    @property",
        "    def output_field(self):",
        "        return CharField()",
        "",
        "# Now you can use: field__upper__contains='TECH'"
    ], "This transform enables case-insensitive comparisons using SQL UPPER()")
    
    # Test the transform
    try:
        upper_search = Entry.objects.filter(headline__upper__contains='TECH').count()
        print(f"   Upper case search results: {upper_search}")
    except Exception as e:
        print(f"   Upper transform error: {e}")
    
    guide.print_header("Create Date Extract Transform", 2)
    guide.print_task("Create a transform that extracts year from date fields")
    guide.print_hint("Use database-specific EXTRACT or YEAR functions")
    guide.wait_for_user()
    
    class ExtractYear(Transform):
        lookup_name = 'extract_year'
        
        def as_sql(self, compiler, connection):
            lhs, lhs_params = compiler.compile(self.lhs)
            if connection.vendor == 'postgresql':
                sql = f"EXTRACT(YEAR FROM {lhs})"
            elif connection.vendor == 'mysql':
                sql = f"YEAR({lhs})"
            else:  # SQLite
                sql = f"strftime('%Y', {lhs})"
            return sql, lhs_params
        
        @property
        def output_field(self):
            return IntegerField()
    
    models.DateField.register_lookup(ExtractYear)
    models.DateTimeField.register_lookup(ExtractYear)
    
    guide.print_solution([
        "class ExtractYear(Transform):",
        "    lookup_name = 'extract_year'",
        "    ",
        "    def as_sql(self, compiler, connection):",
        "        lhs, lhs_params = compiler.compile(self.lhs)",
        "        if connection.vendor == 'postgresql':",
        "            sql = f'EXTRACT(YEAR FROM {lhs})'",
        "        elif connection.vendor == 'mysql':",
        "            sql = f'YEAR({lhs})'",
        "        else:  # SQLite",
        "            sql = f\"strftime('%Y', {lhs})\"",
        "        return sql, lhs_params"
    ], "Custom as_sql() method allows database-specific implementations")
    
    # Test the transform
    try:
        year_extract = Entry.objects.filter(pub_date__extract_year=2024).count()
        print(f"   Year extraction results: {year_extract}")
    except Exception as e:
        print(f"   Year extract error: {e}")


def section_3_custom_lookups(guide):
    """Section 3: Creating Custom Lookups"""
    guide.print_header("Creating Custom Lookups")
    
    print("""
🔍 THEORY: Lookups compare left-hand side (lhs) with right-hand side (rhs).
They generate boolean comparisons in SQL WHERE clauses.

LOOKUP COMPONENTS:
• lookup_name: The name used in queries (e.g., 'ne' for __ne)
• as_sql(): Generates comparison SQL like 'lhs <> rhs'
• process_lhs() and process_rhs(): Process left and right operands
""")
    
    guide.print_header("Create NotEqual Lookup", 2)
    guide.print_task("Create a lookup for 'not equal' comparisons")
    guide.print_hint("Use <> or != operator in SQL, inherit from Lookup class")
    guide.wait_for_user()
    
    class NotEqual(Lookup):
        lookup_name = 'ne'
        
        def as_sql(self, compiler, connection):
            lhs, lhs_params = self.process_lhs(compiler, connection)
            rhs, rhs_params = self.process_rhs(compiler, connection)
            params = lhs_params + rhs_params
            return f'{lhs} <> {rhs}', params
    
    Field.register_lookup(NotEqual)
    
    guide.print_solution([
        "class NotEqual(Lookup):",
        "    lookup_name = 'ne'",
        "    ",
        "    def as_sql(self, compiler, connection):",
        "        lhs, lhs_params = self.process_lhs(compiler, connection)",
        "        rhs, rhs_params = self.process_rhs(compiler, connection)",
        "        params = lhs_params + rhs_params",
        "        return f'{lhs} <> {rhs}', params",
        "",
        "Field.register_lookup(NotEqual)  # Register on all fields"
    ], "Custom lookups generate comparison operators. Use process_lhs/rhs for operands.")
    
    # Test the lookup
    try:
        not_perfect = Entry.objects.filter(rating__ne=5).count()
        print(f"   Entries with rating != 5: {not_perfect}")
    except Exception as e:
        print(f"   NotEqual lookup error: {e}")
    
    guide.print_header("Create Between Lookup", 2)
    guide.print_task("Create a lookup that accepts two values for BETWEEN comparison")
    guide.print_hint("Override __init__ to accept tuple, generate BETWEEN SQL")
    guide.wait_for_user()
    
    class Between(Lookup):
        lookup_name = 'between'
        
        def __init__(self, lhs, rhs):
            if not isinstance(rhs, (tuple, list)) or len(rhs) != 2:
                raise ValueError("Between lookup requires a tuple of two values")
            super().__init__(lhs, rhs)
        
        def as_sql(self, compiler, connection):
            lhs, lhs_params = self.process_lhs(compiler, connection)
            # For BETWEEN, we need to handle the tuple manually
            lower, upper = self.rhs
            sql = f'{lhs} BETWEEN %s AND %s'
            params = lhs_params + [lower, upper]
            return sql, params
    
    IntegerField.register_lookup(Between)
    FloatField.register_lookup(Between)
    models.DecimalField.register_lookup(Between)
    
    guide.print_solution([
        "class Between(Lookup):",
        "    lookup_name = 'between'",
        "    ",
        "    def __init__(self, lhs, rhs):",
        "        if not isinstance(rhs, (tuple, list)) or len(rhs) != 2:",
        "            raise ValueError('Between requires tuple of two values')",
        "        super().__init__(lhs, rhs)",
        "    ",
        "    def as_sql(self, compiler, connection):",
        "        lhs, lhs_params = self.process_lhs(compiler, connection)",
        "        lower, upper = self.rhs",
        "        sql = f'{lhs} BETWEEN %s AND %s'",
        "        params = lhs_params + [lower, upper]",
        "        return sql, params"
    ], "Custom __init__ allows special rhs handling. BETWEEN is inclusive.")
    
    # Test the lookup
    try:
        # Note: This would require special handling in Django's query parsing
        # For demo, we'll use a simpler approach
        between_ratings = Entry.objects.extra(
            where=["rating BETWEEN %s AND %s"],
            params=[3, 4]
        ).count()
        print(f"   Ratings between 3-4: {between_ratings}")
    except Exception as e:
        print(f"   Between lookup error: {e}")
    
    guide.print_header("Create Fuzzy Match Lookup", 2)
    guide.print_task("Create a lookup for fuzzy string matching with tolerance")
    guide.print_hint("Use LIKE with wildcards or Levenshtein distance if available")
    guide.wait_for_user()
    
    class FuzzyMatch(Lookup):
        lookup_name = 'fuzzy'
        
        def as_sql(self, compiler, connection):
            lhs, lhs_params = self.process_lhs(compiler, connection)
            rhs, rhs_params = self.process_rhs(compiler, connection)
            
            # Simple fuzzy matching using LIKE with wildcards
            if isinstance(self.rhs, str):
                fuzzy_pattern = f'%{self.rhs}%'
                sql = f'{lhs} LIKE %s'
                params = lhs_params + [fuzzy_pattern]
            else:
                sql = f'{lhs} LIKE {rhs}'
                params = lhs_params + rhs_params
            
            return sql, params
    
    CharField.register_lookup(FuzzyMatch)
    models.TextField.register_lookup(FuzzyMatch)
    
    guide.print_solution([
        "class FuzzyMatch(Lookup):",
        "    lookup_name = 'fuzzy'",
        "    ",
        "    def as_sql(self, compiler, connection):",
        "        lhs, lhs_params = self.process_lhs(compiler, connection)",
        "        rhs, rhs_params = self.process_rhs(compiler, connection)",
        "        ",
        "        # Simple fuzzy with LIKE and wildcards",
        "        if isinstance(self.rhs, str):",
        "            fuzzy_pattern = f'%{self.rhs}%'",
        "            sql = f'{lhs} LIKE %s'",
        "            params = lhs_params + [fuzzy_pattern]",
        "        else:",
        "            sql = f'{lhs} LIKE {rhs}'",
        "            params = lhs_params + rhs_params",
        "        return sql, params"
    ], "Fuzzy matching can use LIKE patterns or distance algorithms")
    
    # Test the lookup
    try:
        fuzzy_tech = Entry.objects.filter(headline__fuzzy='tech').count()
        print(f"   Fuzzy matches for 'tech': {fuzzy_tech}")
    except Exception as e:
        print(f"   Fuzzy lookup error: {e}")


def section_4_advanced_combinations(guide):
    """Section 4: Advanced Lookup Combinations"""
    guide.print_header("Advanced Lookup Combinations")
    
    print("""
🎯 THEORY: The real power comes from combining transforms and lookups.
You can chain multiple transforms and end with a lookup for complex filtering.

CHAINING EXAMPLES:
• field__transform1__transform2__lookup
• email__domain__upper__contains='TECH'
• date__year__in=[2023, 2024]
""")
    
    guide.print_header("Transform + Lookup Chains", 2)
    guide.print_task("Find entries where headline length is in range 15-30 characters")
    guide.print_hint("Chain the length transform with a range lookup")
    guide.wait_for_user()
    
    try:
        medium_headlines = Entry.objects.filter(headline__length__range=(15, 30)).count()
        long_headlines = Entry.objects.filter(headline__length__gt=25).count()
        
        guide.print_solution([
            "# Transform + Lookup chain:",
            "Entry.objects.filter(headline__length__range=(15, 30))",
            "Entry.objects.filter(headline__length__gt=25)",
            "",
            "# The chain: headline → length() → range(15,30)"
        ], "Transforms modify the field, then lookups compare the result")
        
        print(f"   Medium headlines (15-30 chars): {medium_headlines}")
        print(f"   Long headlines (>25 chars): {long_headlines}")
        
    except Exception as e:
        print(f"   Chain error: {e}")
    
    guide.print_header("Multiple Transform Chains", 2)
    guide.print_task("Create a complex chain: field → upper → length → gte")
    guide.print_hint("Chain transforms can modify data multiple times before lookup")
    guide.wait_for_user()
    
    try:
        # This would be: headline → upper() → length() → gte(20)
        # Meaning: uppercase the headline, get its length, check if >= 20
        complex_chain = Entry.objects.filter(headline__upper__length__gte=20).count()
        
        guide.print_solution([
            "# Multi-transform chain:",
            "Entry.objects.filter(headline__upper__length__gte=20)",
            "",
            "# The chain: headline → UPPER() → LENGTH() → >= 20",
            "# This finds headlines that, when uppercased, are >= 20 chars"
        ], "Multiple transforms can be chained before the final lookup")
        
        print(f"   Complex chain results: {complex_chain}")
        
    except Exception as e:
        print(f"   Multi-chain error: {e}")
    
    guide.print_header("Combining with Q Objects", 2)
    guide.print_task("Use custom lookups in complex Q object expressions")
    guide.print_hint("Combine ne lookup with OR logic using Q objects")
    guide.wait_for_user()
    
    try:
        complex_q = Entry.objects.filter(
            Q(rating__ne=3) & 
            (Q(headline__length__gt=20) | Q(number_of_comments__gte=30))
        ).count()
        
        guide.print_solution([
            "# Custom lookups in Q expressions:",
            "Entry.objects.filter(",
            "    Q(rating__ne=3) & ",
            "    (Q(headline__length__gt=20) | Q(number_of_comments__gte=30))",
            ")",
            "",
            "# Logic: (rating != 3) AND (long_headline OR many_comments)"
        ], "Custom lookups work seamlessly with Q objects for complex logic")
        
        print(f"   Complex Q filter results: {complex_q}")
        
    except Exception as e:
        print(f"   Q object error: {e}")
    
    guide.print_header("Performance Considerations", 2)
    guide.print_task("Compare performance of custom vs built-in lookups")
    guide.print_hint("Measure execution time and consider database load")
    guide.wait_for_user()
    
    import time
    
    try:
        # Test built-in vs custom performance
        start = time.time()
        builtin_result = Entry.objects.exclude(rating=5).count()
        builtin_time = time.time() - start
        
        start = time.time()
        custom_result = Entry.objects.filter(rating__ne=5).count()
        custom_time = time.time() - start
        
        guide.print_solution([
            "# Performance comparison:",
            "import time",
            "",
            "start = time.time()",
            "builtin = Entry.objects.exclude(rating=5).count()",
            "builtin_time = time.time() - start",
            "",
            "start = time.time()",
            "custom = Entry.objects.filter(rating__ne=5).count()",
            "custom_time = time.time() - start"
        ], "Always measure performance. Built-ins are usually optimized.")
        
        print(f"   Built-in exclude: {builtin_result} in {builtin_time:.4f}s")
        print(f"   Custom ne lookup: {custom_result} in {custom_time:.4f}s")
        
    except Exception as e:
        print(f"   Performance test error: {e}")


def section_5_real_world_applications(guide):
    """Section 5: Real-world Applications"""
    guide.print_header("Real-world Applications")
    
    print("""
🌟 PRACTICAL SCENARIOS: Apply custom lookups to solve real business problems.
Learn when to create custom components vs using built-in alternatives.

COMMON USE CASES:
• Search functionality with tolerance
• Data validation and cleaning
• Business logic implementation
• Performance optimization
• Database-specific features
""")
    
    guide.print_header("Search with Tolerance", 2)
    guide.print_task("Implement flexible search that finds partial matches")
    guide.print_hint("Combine fuzzy matching with case-insensitive search")
    guide.wait_for_user()
    
    def flexible_search(query_term):
        """Implement flexible search strategy."""
        # Strategy 1: Exact match (highest priority)
        exact = Entry.objects.filter(headline__iexact=query_term)
        
        # Strategy 2: Contains match
        contains = Entry.objects.filter(headline__icontains=query_term)
        
        # Strategy 3: Fuzzy match
        fuzzy = Entry.objects.filter(headline__fuzzy=query_term)
        
        # Strategy 4: Word-level search
        words = query_term.split()
        word_search = Entry.objects.filter(
            Q(headline__icontains=words[0]) if words else Q()
        )
        for word in words[1:]:
            word_search = word_search.filter(headline__icontains=word)
        
        return {
            'exact': exact.count(),
            'contains': contains.count(),
            'fuzzy': fuzzy.count(),
            'word_level': word_search.count()
        }
    
    search_results = flexible_search('tech review')
    
    guide.print_solution([
        "def flexible_search(query_term):",
        "    # 1. Exact match (highest relevance)",
        "    exact = Entry.objects.filter(headline__iexact=query_term)",
        "    ",
        "    # 2. Contains match",
        "    contains = Entry.objects.filter(headline__icontains=query_term)",
        "    ",
        "    # 3. Fuzzy match (custom lookup)",
        "    fuzzy = Entry.objects.filter(headline__fuzzy=query_term)",
        "    ",
        "    # 4. Word-level search",
        "    words = query_term.split()",
        "    word_search = Entry.objects.all()",
        "    for word in words:",
        "        word_search = word_search.filter(headline__icontains=word)"
    ], "Flexible search combines multiple strategies with relevance ranking")
    
    print(f"   Search results for 'tech review':")
    for strategy, count in search_results.items():
        print(f"     {strategy}: {count}")
    
    guide.print_header("Data Validation Lookups", 2)
    guide.print_task("Create lookups for common validation scenarios")
    guide.print_hint("Email format, phone numbers, strong passwords")
    guide.wait_for_user()
    
    class ValidEmail(Lookup):
        lookup_name = 'valid_email'
        
        def as_sql(self, compiler, connection):
            lhs, lhs_params = self.process_lhs(compiler, connection)
            # Simple email validation pattern
            if self.rhs:
                sql = f"{lhs} LIKE '%@%.%'"
            else:
                sql = f"{lhs} NOT LIKE '%@%.%'"
            return sql, lhs_params
    
    CharField.register_lookup(ValidEmail)
    
    guide.print_solution([
        "class ValidEmail(Lookup):",
        "    lookup_name = 'valid_email'",
        "    ",
        "    def as_sql(self, compiler, connection):",
        "        lhs, lhs_params = self.process_lhs(compiler, connection)",
        "        if self.rhs:",
        "            sql = f\"{lhs} LIKE '%@%.%'\"",
        "        else:",
        "            sql = f\"{lhs} NOT LIKE '%@%.%'\"",
        "        return sql, lhs_params",
        "",
        "# Usage: Author.objects.filter(email__valid_email=True)"
    ], "Validation lookups help maintain data quality at the database level")
    
    try:
        valid_emails = Author.objects.extra(
            where=["email LIKE '%@%.%'"]
        ).count()
        print(f"   Authors with valid email format: {valid_emails}")
    except Exception as e:
        print(f"   Validation error: {e}")
    
    guide.print_header("Business Logic Implementation", 2)
    guide.print_task("Create a lookup for 'business hours' filtering")
    guide.print_hint("Check if a datetime falls within business hours (9 AM - 5 PM)")
    guide.wait_for_user()
    
    class BusinessHours(Lookup):
        lookup_name = 'business_hours'
        
        def as_sql(self, compiler, connection):
            lhs, lhs_params = self.process_lhs(compiler, connection)
            
            if connection.vendor == 'postgresql':
                sql = f"EXTRACT(HOUR FROM {lhs}) BETWEEN 9 AND 17"
            elif connection.vendor == 'mysql':
                sql = f"HOUR({lhs}) BETWEEN 9 AND 17"
            else:  # SQLite
                sql = f"CAST(strftime('%H', {lhs}) AS INTEGER) BETWEEN 9 AND 17"
            
            return sql, lhs_params
    
    models.DateTimeField.register_lookup(BusinessHours)
    
    guide.print_solution([
        "class BusinessHours(Lookup):",
        "    lookup_name = 'business_hours'",
        "    ",
        "    def as_sql(self, compiler, connection):",
        "        lhs, lhs_params = self.process_lhs(compiler, connection)",
        "        ",
        "        if connection.vendor == 'postgresql':",
        "            sql = f'EXTRACT(HOUR FROM {lhs}) BETWEEN 9 AND 17'",
        "        elif connection.vendor == 'mysql':",
        "            sql = f'HOUR({lhs}) BETWEEN 9 AND 17'",
        "        else:  # SQLite",
        "            sql = f\"CAST(strftime('%H', {lhs}) AS INTEGER) BETWEEN 9 AND 17\"",
        "        ",
        "        return sql, lhs_params"
    ], "Business logic lookups encode domain rules into the database layer")
    
    print("   Business hours lookup created for datetime fields")


def main():
    """Main interactive practice session."""
    guide = LookupsPracticeGuide()
    
    print("🔍 Django Lookups Interactive Practice Guide")
    print("Following: https://docs.djangoproject.com/en/5.2/ref/models/lookups/")
    print("="*80)
    print("""
🎯 LEARNING OBJECTIVES:
• Master all built-in Django lookups (30+ types)
• Create custom Transform classes for data modification
• Implement custom Lookup classes for comparisons
• Chain transforms and lookups for complex filtering
• Apply lookups to real-world scenarios
• Understand performance implications

📋 PRACTICE SECTIONS:
1. Built-in Lookups Mastery - All lookup types with examples
2. Custom Transforms - Data modification before comparison
3. Custom Lookups - Custom comparison operators
4. Advanced Combinations - Chaining and complex logic
5. Real-world Applications - Practical scenarios

💡 TIPS:
• Understand the difference between Transform and Lookup
• Practice chaining for complex data processing
• Consider performance implications of custom components
• Test with different database backends
• Use for business logic implementation

🔧 LOOKUP STRUCTURE:
   field__transform1__transform2__lookup=value
   │     │            │          │
   │     │            │          └─ Final comparison
   │     │            └─ Second modification
   │     └─ First modification
   └─ Original field
""")
    
    choice = input("\n🚀 Ready to master Django Lookups? (y/n): ").lower()
    if choice != 'y':
        print("Come back when you're ready to explore Django's lookup system! 🔍")
        return
    
    try:
        # Run all practice sections
        section_1_builtin_lookups_mastery(guide)
        section_2_custom_transforms(guide)
        section_3_custom_lookups(guide)
        section_4_advanced_combinations(guide)
        section_5_real_world_applications(guide)
        
        print("\n" + "="*80)
        print("🎉 CONGRATULATIONS! Django Lookups Mastery Complete!")
        print("="*80)
        print("""
✅ YOU HAVE MASTERED:
• All 30+ built-in Django lookup types
• Custom Transform creation and registration
• Custom Lookup implementation patterns
• Transform and lookup chaining techniques
• Real-world application scenarios
• Performance optimization strategies

🧠 KEY CONCEPTS LEARNED:
• Query Expression API implementation
• RegisterLookupMixin usage patterns
• Database vendor-specific SQL generation
• Transform vs Lookup architectural differences
• Chaining mechanisms and data flow
• Business logic integration strategies

🔧 CUSTOM COMPONENTS CREATED:
• Length Transform - Calculate text length
• Upper Transform - Text case conversion
• ExtractYear Transform - Date component extraction
• NotEqual Lookup - Custom comparison operator
• Between Lookup - Range comparison with tuples
• FuzzyMatch Lookup - Flexible text matching
• ValidEmail Lookup - Data validation
• BusinessHours Lookup - Business logic implementation

🚀 NEXT STEPS:
• Apply custom lookups to your projects
• Explore database-specific features
• Create domain-specific lookup libraries
• Optimize query performance
• Build advanced search functionality

🎓 You're now equipped to extend Django's ORM with custom lookups!
""")
        
    except KeyboardInterrupt:
        print("\n\n⏸️  Practice session interrupted. Resume anytime!")
    except Exception as e:
        print(f"\n❌ Error during practice: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
