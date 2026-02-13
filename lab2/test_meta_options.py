#!/usr/bin/env python
"""
Django Model Meta Options Test Script
Demonstrates all Meta options in practice

Run this script to see how Django Meta options work:
python test_meta_options.py
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modelspractice.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import connection
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from meta_practice.models import (
    BlogPost, Category, Tag, Question, Answer,
    PublishedBlogPost, Product, ConfigurableModel,
    CompleteExampleModel, LegacyModel, TimestampedModel
)


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")


def print_section(title):
    """Print a formatted section."""
    print(f"\n{'─'*40}")
    print(f"📋 {title}")
    print(f"{'─'*40}")


def inspect_meta_options():
    """Inspect and display Meta options for all models."""
    print_header("DJANGO MODEL META OPTIONS INSPECTION")
    
    models = [
        BlogPost, Category, Tag, Question, Answer,
        PublishedBlogPost, Product, ConfigurableModel,
        CompleteExampleModel, LegacyModel
    ]
    
    for model in models:
        print_section(f"{model.__name__} Meta Options")
        meta = model._meta
        
        print(f"📦 Model Name: {meta.model_name}")
        print(f"📝 Verbose Name: {meta.verbose_name}")
        print(f"📝 Verbose Name Plural: {meta.verbose_name_plural}")
        print(f"🗄️  Database Table: {meta.db_table}")
        print(f"📊 Ordering: {meta.ordering}")
        print(f"⏰ Get Latest By: {meta.get_latest_by}")
        print(f"🔧 Abstract: {meta.abstract}")
        print(f"🔄 Proxy: {meta.proxy}")
        print(f"⚙️  Managed: {meta.managed}")
        print(f"🔐 Default Permissions: {meta.default_permissions}")
        
        # Custom permissions
        if hasattr(meta, 'permissions') and meta.permissions:
            print(f"🔒 Custom Permissions:")
            for perm_code, perm_name in meta.permissions:
                print(f"   - {perm_code}: {perm_name}")
        
        # Indexes
        if hasattr(meta, 'indexes') and meta.indexes:
            print(f"📈 Indexes: {len(meta.indexes)} defined")
            for i, index in enumerate(meta.indexes, 1):
                print(f"   {i}. {index.name or 'auto'}: {index.fields}")
        
        # Constraints
        if hasattr(meta, 'constraints') and meta.constraints:
            print(f"🔒 Constraints: {len(meta.constraints)} defined")
            for i, constraint in enumerate(meta.constraints, 1):
                print(f"   {i}. {constraint.name}: {type(constraint).__name__}")


def test_abstract_inheritance():
    """Test abstract base class inheritance."""
    print_header("ABSTRACT BASE CLASS INHERITANCE")
    
    # TimestampedModel is abstract, so we can't instantiate it
    print("🔍 TimestampedModel is abstract - cannot create instances")
    print(f"   Abstract: {TimestampedModel._meta.abstract}")
    
    # But BlogPost inherits from it
    print("✅ BlogPost inherits from TimestampedModel")
    print(f"   Has 'created' field: {'created' in [f.name for f in BlogPost._meta.fields]}")
    print(f"   Has 'modified' field: {'modified' in [f.name for f in BlogPost._meta.fields]}")
    print(f"   get_latest_by: {BlogPost._meta.get_latest_by}")


def test_custom_table_names():
    """Test custom table names and database options."""
    print_header("CUSTOM TABLE NAMES & DATABASE OPTIONS")
    
    # Check actual table names in database
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%practice%';")
        tables = cursor.fetchall()
        
        print("🗄️  Database tables for meta_practice app:")
        for table in tables:
            table_name = table[0]
            print(f"   - {table_name}")
            
            # Check if it's our custom table
            if table_name == 'custom_blog_posts':
                print(f"     ✅ BlogPost uses custom table name: {table_name}")
            elif table_name == 'complete_example':
                print(f"     ✅ CompleteExampleModel uses custom table name: {table_name}")


def test_ordering_behavior():
    """Test Meta ordering behavior."""
    print_header("ORDERING BEHAVIOR")
    
    # Create some test data if not exists
    user, _ = User.objects.get_or_create(username='testuser')
    category, _ = Category.objects.get_or_create(name='Test Category')
    
    # Test Category ordering
    print_section("Category Ordering")
    categories = Category.objects.all()
    print(f"📊 Category ordering: {Category._meta.ordering}")
    print(f"   Query will order by: {categories.query.order_by}")
    
    # Test Tag ordering
    print_section("Tag Ordering")
    tags = Tag.objects.all()
    print(f"📊 Tag ordering: {Tag._meta.ordering}")
    print(f"   Query will order by: {tags.query.order_by}")


def test_permissions():
    """Test custom permissions."""
    print_header("CUSTOM PERMISSIONS")
    
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import Permission
    
    # Check BlogPost permissions
    print_section("BlogPost Custom Permissions")
    blog_ct = ContentType.objects.get_for_model(BlogPost)
    blog_perms = Permission.objects.filter(content_type=blog_ct)
    
    print("🔐 BlogPost permissions:")
    for perm in blog_perms:
        print(f"   - {perm.codename}: {perm.name}")
    
    # Check Product permissions
    print_section("Product Custom Permissions")
    product_ct = ContentType.objects.get_for_model(Product)
    product_perms = Permission.objects.filter(content_type=product_ct)
    
    print("🔐 Product permissions:")
    for perm in product_perms:
        print(f"   - {perm.codename}: {perm.name}")


def test_proxy_model():
    """Test proxy model behavior."""
    print_header("PROXY MODEL BEHAVIOR")
    
    user, _ = User.objects.get_or_create(username='testuser')
    
    # Create a blog post
    blog_post, created = BlogPost.objects.get_or_create(
        title="Test Published Post",
        defaults={
            'slug': 'test-published-post',
            'content': 'This is a test post',
            'author': user,
            'published': True,
            'views_count': 100
        }
    )
    
    print("📊 Proxy Model Comparison:")
    print(f"   BlogPost table: {BlogPost._meta.db_table}")
    print(f"   PublishedBlogPost table: {PublishedBlogPost._meta.db_table}")
    print(f"   Same table: {BlogPost._meta.db_table == PublishedBlogPost._meta.db_table}")
    
    print(f"\n📈 Ordering differences:")
    print(f"   BlogPost ordering: {BlogPost._meta.ordering}")
    print(f"   PublishedBlogPost ordering: {PublishedBlogPost._meta.ordering}")
    
    # Test proxy model method
    published_post = PublishedBlogPost.objects.get(id=blog_post.id)
    analytics = published_post.get_analytics_data()
    print(f"\n📊 Analytics from proxy model:")
    print(f"   Views: {analytics['views']}")
    print(f"   Author: {analytics['author']}")
    print(f"   Days since published: {analytics['days_since_published']}")


def test_constraints():
    """Test model constraints."""
    print_header("MODEL CONSTRAINTS")
    
    print_section("Testing Check Constraints")
    
    user, _ = User.objects.get_or_create(username='testuser')
    category, _ = Category.objects.get_or_create(name='Test Category')
    
    # Test Product constraints
    try:
        product = Product(
            name="Invalid Product",
            sku="TEST001",
            price=-10.00,  # This should violate positive_price constraint
            category=category,
            stock_quantity=5
        )
        product.full_clean()  # This will check constraints
        print("❌ Expected constraint violation for negative price")
    except ValidationError as e:
        print("✅ Constraint validation working - negative price rejected")
    
    # Test Answer constraints
    question, _ = Question.objects.get_or_create(
        text="Test question?",
        category=category,
        author=user
    )
    
    try:
        answer = Answer(
            question=question,
            text="Test answer",
            author=user,
            votes=150  # This should violate votes range constraint
        )
        answer.full_clean()
        print("❌ Expected constraint violation for votes > 100")
    except ValidationError as e:
        print("✅ Constraint validation working - votes > 100 rejected")


def test_order_with_respect_to():
    """Test order_with_respect_to functionality."""
    print_header("ORDER WITH RESPECT TO")
    
    user, _ = User.objects.get_or_create(username='testuser')
    category, _ = Category.objects.get_or_create(name='Test Category')
    
    # Create a question
    question, created = Question.objects.get_or_create(
        text="What is Django?",
        category=category,
        author=user
    )
    
    # Create some answers
    answers_data = [
        "Django is a web framework",
        "Django is written in Python",
        "Django follows MTV pattern"
    ]
    
    answers = []
    for answer_text in answers_data:
        answer, created = Answer.objects.get_or_create(
            question=question,
            text=answer_text,
            author=user
        )
        answers.append(answer)
    
    print("📋 Order with respect to demonstration:")
    print(f"   Question: {question.text}")
    print(f"   Number of answers: {answers[0].__class__.objects.filter(question=question).count()}")
    
    # Show ordering methods
    print(f"\n📊 Answer ordering methods available:")
    print(f"   - get_answer_order() on Question")
    print(f"   - set_answer_order() on Question") 
    print(f"   - get_next_in_order() on Answer")
    print(f"   - get_previous_in_order() on Answer")
    
    if hasattr(question, 'get_answer_order'):
        try:
            order = question.get_answer_order()
            print(f"   Current answer order: {order}")
        except Exception as e:
            print(f"   Order method exists but needs data: {e}")


def test_unique_together():
    """Test unique_together constraint."""
    print_header("UNIQUE TOGETHER CONSTRAINTS")
    
    # Test LegacyModel unique_together
    print_section("LegacyModel unique_together")
    
    try:
        # Create first instance
        legacy1 = LegacyModel.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="123-456-7890"
        )
        print("✅ First instance created successfully")
        
        # Try to create duplicate (should fail)
        legacy2 = LegacyModel(
            name="John Doe",
            email="john@example.com",  # Same name + email combination
            phone="987-654-3210"
        )
        legacy2.full_clean()
        legacy2.save()
        print("❌ Expected unique_together violation")
        
    except (ValidationError, IntegrityError) as e:
        print("✅ unique_together constraint working - duplicate rejected")
    except Exception as e:
        print(f"ℹ️  Note: {e}")


def test_custom_managers():
    """Test custom manager behavior."""
    print_header("CUSTOM MANAGERS")
    
    # Test ConfigurableModel managers
    print_section("ConfigurableModel Managers")
    
    # Create some test data
    ConfigurableModel.objects.get_or_create(name="High Priority", priority=10, is_active=True)
    ConfigurableModel.objects.get_or_create(name="Low Priority", priority=1, is_active=True)
    ConfigurableModel.objects.get_or_create(name="Inactive Item", priority=5, is_active=False)
    
    print("📊 Available managers:")
    print(f"   - objects (default): {type(ConfigurableModel.objects).__name__}")
    print(f"   - custom: {type(ConfigurableModel.custom).__name__}")
    
    print(f"\n🔍 Manager behavior:")
    print(f"   All objects count: {ConfigurableModel.objects.count()}")
    print(f"   Active objects count: {ConfigurableModel.custom.active().count()}")
    
    print(f"\n📈 Custom ordering (by_priority):")
    for obj in ConfigurableModel.custom.by_priority()[:3]:
        print(f"   - {obj.name} (priority: {obj.priority})")


def test_get_latest_by():
    """Test get_latest_by functionality."""
    print_header("GET LATEST BY")
    
    user, _ = User.objects.get_or_create(username='testuser')
    category, _ = Category.objects.get_or_create(name='Test Category')
    
    # Create some blog posts
    for i in range(3):
        BlogPost.objects.get_or_create(
            title=f"Post {i+1}",
            slug=f"post-{i+1}",
            content=f"Content for post {i+1}",
            author=user
        )
    
    print_section("Testing get_latest_by")
    
    try:
        latest_post = BlogPost.objects.latest()
        print(f"✅ Latest blog post: {latest_post.title}")
        print(f"   Created: {latest_post.created}")
        print(f"   get_latest_by field: {BlogPost._meta.get_latest_by}")
        
        earliest_post = BlogPost.objects.earliest()
        print(f"✅ Earliest blog post: {earliest_post.title}")
        print(f"   Created: {earliest_post.created}")
        
    except Exception as e:
        print(f"❌ Error testing latest/earliest: {e}")


def run_all_tests():
    """Run all Meta options tests."""
    print("🚀 Starting Django Model Meta Options Tests")
    print(f"⏰ Test started at: {datetime.now()}")
    
    test_functions = [
        inspect_meta_options,
        test_abstract_inheritance,
        test_custom_table_names,
        test_ordering_behavior,
        test_permissions,
        test_proxy_model,
        test_constraints,
        test_order_with_respect_to,
        test_unique_together,
        test_custom_managers,
        test_get_latest_by,
    ]
    
    for test_func in test_functions:
        try:
            test_func()
        except Exception as e:
            print(f"❌ Error in {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print_header("TESTS COMPLETED")
    print(f"⏰ Test completed at: {datetime.now()}")
    print("🎉 All Django Meta Options tests finished!")


if __name__ == "__main__":
    run_all_tests()
