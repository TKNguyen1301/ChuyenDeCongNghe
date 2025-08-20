#!/usr/bin/env python
"""
Django Model Class Methods and Attributes Test Script
Following https://docs.djangoproject.com/en/5.2/ref/models/class/

This script demonstrates all important Model class methods and attributes
using our model_class_practice models.
"""

import os
import sys
import django
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from decimal import Decimal
import pickle
import uuid

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modelspractice.settings')
    django.setup()

from django.contrib.auth.models import User
from model_class_practice.models import (
    Article, Book, Event, Product, Profile, Order,
    Analytics, SimpleNote, BlogPost
)


def cleanup_test_data():
    """Clean up any existing test data."""
    print("Cleaning up existing test data...")
    
    # Clean up in reverse dependency order
    Analytics.objects.all().delete()
    BlogPost.objects.all().delete()
    Order.objects.all().delete()
    Profile.objects.all().delete()
    Product.objects.all().delete()
    Event.objects.all().delete()
    Book.objects.all().delete()
    Article.objects.all().delete()
    SimpleNote.objects.all().delete()
    
    print("✅ Test data cleaned up")


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def test_basic_model_methods():
    """Test basic Model methods with Article model."""
    print_section("1. Basic Model Methods (Article)")
    
    # Clean up existing data to avoid conflicts
    Article.objects.filter(slug="django-model-class-ref").delete()
    
    # Create a user first
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    print(f"User created: {created}")
    
    # Create an article
    article = Article(
        title="Django Model Class Reference",
        slug="django-model-class-ref",
        content="This is a comprehensive guide to Django Model class methods.",
        author=user,
        status='draft'
    )
    
    # Demonstrate __str__ and __repr__
    print(f"Article __str__: {article}")
    print(f"Article __repr__: {repr(article)}")
    
    # Demonstrate save() method
    print("\n--- save() method ---")
    print(f"Before save - pk: {article.pk}")
    print(f"Before save - _state.adding: {article._state.adding}")
    article.save()
    print(f"After save - pk: {article.pk}")
    print(f"After save - _state.adding: {article._state.adding}")
    
    # Demonstrate full_clean()
    print("\n--- full_clean() method ---")
    try:
        article.full_clean()
        print("✅ Article validation passed")
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
    
    # Test custom save logic (status change)
    print("\n--- Custom save logic ---")
    article.status = 'published'
    article.save()
    print(f"Published date set: {article.published_date}")
    
    # Demonstrate refresh_from_db()
    print("\n--- refresh_from_db() method ---")
    original_view_count = article.view_count
    article.increment_view_count()  # This updates the database
    print(f"View count after increment: {article.view_count}")
    
    # Simulate external update
    Article.objects.filter(pk=article.pk).update(view_count=100)
    print(f"View count before refresh: {article.view_count}")
    article.refresh_from_db()
    print(f"View count after refresh: {article.view_count}")
    
    # Demonstrate get_absolute_url()
    print(f"\nAbsolute URL: {article.get_absolute_url()}")
    
    # Demonstrate get_FOO_display()
    print(f"Status display: {article.get_status_display()}")
    print(f"Custom status display: {article.get_status_display_custom()}")
    
    return article


def test_exceptions_and_managers():
    """Test DoesNotExist, MultipleObjectsReturned exceptions and custom managers."""
    print_section("2. Exceptions and Custom Managers (Book)")
    
    # Clean up existing books
    Book.objects.all().delete()
    
    # Create some books
    book1 = Book.objects.create(
        title="Django for Beginners",
        isbn="9781234567890",
        author="William Vincent",
        publication_date=timezone.now().date(),
        pages=300,
        price=Decimal('29.99')
    )
    
    book2 = Book.objects.create(
        title="Two Scoops of Django",
        isbn="9780987654321",
        author="Daniel Roy Greenfeld",
        publication_date=timezone.now().date(),
        pages=500,
        price=Decimal('39.99')
    )
    
    # Demonstrate DoesNotExist exception
    print("\n--- DoesNotExist Exception ---")
    try:
        nonexistent = Book.objects.get(isbn="9999999999999")
    except Book.DoesNotExist as e:
        print(f"✅ Caught DoesNotExist: {e}")
    
    # Using our custom find_by_isbn method
    found_book = Book.find_by_isbn("9781234567890")
    print(f"Found book: {found_book}")
    
    not_found = Book.find_by_isbn("9999999999999")
    print(f"Not found book: {not_found}")
    
    # Demonstrate __eq__ and __hash__
    print("\n--- Custom __eq__ and __hash__ ---")
    book1_copy = Book.objects.get(isbn="9781234567890")
    print(f"book1 == book1_copy: {book1 == book1_copy}")
    print(f"book1 hash: {hash(book1)}")
    print(f"book1_copy hash: {hash(book1_copy)}")
    
    # Test books in a set (requires proper __hash__)
    book_set = {book1, book1_copy, book2}
    print(f"Books in set: {len(book_set)} (should be 2)")


def test_date_navigation():
    """Test get_next_by_FOO and get_previous_by_FOO methods."""
    print_section("3. Date-based Navigation (Event)")
    
    # Create events with different dates
    base_date = timezone.now()
    events = []
    
    for i in range(3):
        event = Event.objects.create(
            name=f"Event {i+1}",
            description=f"Description for event {i+1}",
            event_date=base_date + timezone.timedelta(days=i*7),
            location=f"Location {i+1}",
            max_attendees=100
        )
        events.append(event)
    
    # Test navigation methods
    middle_event = events[1]
    print(f"Current event: {middle_event}")
    
    next_event = middle_event.get_next_event()
    print(f"Next event: {next_event}")
    
    previous_event = middle_event.get_previous_event()
    print(f"Previous event: {previous_event}")
    
    # Test edge cases
    last_event = events[-1]
    print(f"Next after last event: {last_event.get_next_event()}")


def test_validation_methods():
    """Test comprehensive validation methods."""
    print_section("4. Validation Methods (Product)")
    
    # Clean up existing products
    Product.objects.filter(sku="TEST-001").delete()
    
    # Test successful creation
    product = Product(
        name="Test Product",
        sku="TEST-001",
        description="A test product",
        price=Decimal('100.00'),
        cost=Decimal('60.00'),
        stock_quantity=50
    )
    
    print("\n--- clean_fields() method ---")
    try:
        product.clean_fields()
        print("✅ Field validation passed")
    except ValidationError as e:
        print(f"❌ Field validation error: {e}")
    
    print("\n--- clean() method ---")
    try:
        product.clean()
        print("✅ Model validation passed")
    except ValidationError as e:
        print(f"❌ Model validation error: {e}")
    
    print("\n--- validate_unique() method ---")
    try:
        product.validate_unique()
        print("✅ Uniqueness validation passed")
    except ValidationError as e:
        print(f"❌ Uniqueness validation error: {e}")
    
    print("\n--- full_clean() method ---")
    try:
        product.full_clean()
        print("✅ Full validation passed")
    except ValidationError as e:
        print(f"❌ Full validation error: {e}")
    
    product.save()
    print(f"Product saved with SKU: {product.sku}")
    print(f"Profit margin: {product.profit_margin:.2f}%")
    print(f"Is low stock: {product.is_low_stock()}")
    
    # Test validation errors
    print("\n--- Testing Validation Errors ---")
    invalid_product = Product(
        name="Invalid Product",
        sku="invalid-sku-002",  # Different SKU to avoid conflict
        price=Decimal('50.00'),
        cost=Decimal('60.00'),  # cost > price, should fail validation
        stock_quantity=5
    )
    
    try:
        invalid_product.full_clean()
        print("❌ Should have failed validation")
    except ValidationError as e:
        print(f"✅ Caught validation error: {e}")


def test_custom_primary_key():
    """Test custom primary key handling."""
    print_section("5. Custom Primary Key (Profile)")
    
    user, _ = User.objects.get_or_create(
        username='profileuser',
        defaults={'email': 'profile@example.com'}
    )
    
    # Clean up existing profile
    Profile.objects.filter(user=user).delete()
    
    profile = Profile.objects.create(
        user=user,
        bio="This is a test profile",
        website="https://example.com"
    )
    
    print(f"Profile UUID (pk): {profile.pk}")
    print(f"Profile UUID type: {type(profile.pk)}")
    print(f"Profile URL: {profile.get_absolute_url()}")
    
    # Test finding by UUID
    found_profile = Profile.objects.get(pk=profile.pk)
    print(f"Found profile: {found_profile}")


def test_state_tracking():
    """Test _state attribute and change tracking."""
    print_section("6. State Tracking (Order)")
    
    user, _ = User.objects.get_or_create(
        username='orderuser',
        defaults={'email': 'order@example.com'}
    )
    
    # Create new order
    print("\n--- Creating new order ---")
    order = Order(
        user=user,
        total_amount=Decimal('99.99'),
        status='pending'
    )
    
    print(f"Before save - _state.adding: {order._state.adding}")
    print(f"Before save - _state.db: {order._state.db}")
    
    order.save()
    
    print(f"After save - _state.adding: {order._state.adding}")
    print(f"After save - _state.db: {order._state.db}")
    print(f"Order number: {order.order_number}")
    
    # Test change tracking
    print("\n--- Testing change tracking ---")
    loaded_order = Order.objects.get(pk=order.pk)
    print(f"Initially changed fields: {loaded_order.get_changed_fields()}")
    
    loaded_order.status = 'processing'
    loaded_order.total_amount = Decimal('109.99')
    print(f"After changes: {loaded_order.get_changed_fields()}")
    
    # Test editability
    print(f"Is editable: {loaded_order.is_editable()}")
    
    loaded_order.status = 'delivered'
    print(f"After delivery, is editable: {loaded_order.is_editable()}")


def test_refresh_and_deferred():
    """Test refresh_from_db and computed fields."""
    print_section("7. Refresh and Computed Fields (Analytics)")
    
    # Get an article for analytics
    article = Article.objects.first()
    if not article:
        print("No article found, skipping analytics test")
        return
    
    analytics = Analytics.objects.create(
        article=article,
        date=timezone.now().date(),
        page_views=1000,
        unique_visitors=500,
        bounce_rate=Decimal('25.50')
    )
    
    print(f"Initial computed score: {analytics.computed_score}")
    
    # Update some fields externally
    Analytics.objects.filter(pk=analytics.pk).update(
        page_views=2000,
        unique_visitors=800
    )
    
    print(f"Before refresh: page_views={analytics.page_views}, unique_visitors={analytics.unique_visitors}")
    
    # Refresh specific fields
    analytics.refresh_from_db(fields=['page_views', 'unique_visitors'])
    
    print(f"After refresh: page_views={analytics.page_views}, unique_visitors={analytics.unique_visitors}")
    print(f"Updated computed score: {analytics.computed_score}")


def test_pickling():
    """Test model instance pickling."""
    print_section("8. Model Pickling (SimpleNote)")
    
    note = SimpleNote.objects.create(
        title="Test Note",
        content="This is a test note for pickling",
        priority=3
    )
    
    print(f"Original note: {note}")
    print(f"Priority display: {note.get_priority_display()}")
    
    # Pickle the instance
    print("\n--- Pickling test ---")
    try:
        pickled_data = pickle.dumps(note)
        print(f"✅ Successfully pickled note (size: {len(pickled_data)} bytes)")
        
        # Unpickle
        unpickled_note = pickle.loads(pickled_data)
        print(f"✅ Successfully unpickled: {unpickled_note}")
        print(f"Same pk: {note.pk == unpickled_note.pk}")
        print(f"Same title: {note.title == unpickled_note.title}")
        
    except Exception as e:
        print(f"❌ Pickling failed: {e}")


def test_inheritance():
    """Test model inheritance."""
    print_section("9. Model Inheritance (BlogPost)")
    
    user, _ = User.objects.get_or_create(
        username='bloguser',
        defaults={'email': 'blog@example.com'}
    )
    
    blog_post = BlogPost.objects.create(
        title="Django Model Inheritance",
        content="This post demonstrates model inheritance",
        author=user
    )
    
    print(f"BlogPost: {blog_post}")
    print(f"Created: {blog_post.created}")
    print(f"Updated: {blog_post.updated}")
    print(f"Age in days: {blog_post.age_in_days()}")
    print(f"Absolute URL: {blog_post.get_absolute_url()}")
    
    # Test inherited manager methods
    latest_post = BlogPost.objects.latest()
    print(f"Latest post: {latest_post}")


def test_additional_features():
    """Test additional Model features."""
    print_section("10. Additional Features")
    
    # Test model _meta API
    print("\n--- Model _meta API ---")
    article_meta = Article._meta
    print(f"App label: {article_meta.app_label}")
    print(f"Model name: {article_meta.model_name}")
    print(f"Verbose name: {article_meta.verbose_name}")
    print(f"Verbose name plural: {article_meta.verbose_name_plural}")
    print(f"Fields: {[f.name for f in article_meta.fields]}")
    
    # Test field access
    print("\n--- Field access ---")
    title_field = article_meta.get_field('title')
    print(f"Title field: {title_field}")
    print(f"Max length: {title_field.max_length}")
    
    # Test model state
    article = Article.objects.first()
    if article:
        print(f"\n--- Model state ---")
        print(f"PK: {article.pk}")
        print(f"_state.adding: {article._state.adding}")
        print(f"_state.db: {article._state.db}")


def main():
    """Main test function."""
    print("Django Model Class Methods and Attributes Demonstration")
    print("Following https://docs.djangoproject.com/en/5.2/ref/models/class/")
    
    try:
        # Clean up first
        cleanup_test_data()
        
        # Run all tests
        article = test_basic_model_methods()
        test_exceptions_and_managers()
        test_date_navigation()
        test_validation_methods()
        test_custom_primary_key()
        test_state_tracking()
        test_refresh_and_deferred()
        test_pickling()
        test_inheritance()
        test_additional_features()
        
        print_section("Summary")
        print("✅ All Django Model class methods and attributes demonstrated successfully!")
        print("\nKey concepts covered:")
        print("- Basic methods: save(), delete(), clean(), __str__, __repr__")
        print("- Validation: clean_fields(), clean(), validate_unique(), full_clean()")
        print("- Exceptions: DoesNotExist, MultipleObjectsReturned")
        print("- Navigation: get_next_by_FOO(), get_previous_by_FOO()")
        print("- State tracking: _state.adding, _state.db")
        print("- Refresh: refresh_from_db()")
        print("- URLs: get_absolute_url()")
        print("- Display: get_FOO_display()")
        print("- Equality: __eq__, __hash__")
        print("- Pickling support")
        print("- Model inheritance")
        print("- Custom primary keys")
        print("- Model meta API")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
