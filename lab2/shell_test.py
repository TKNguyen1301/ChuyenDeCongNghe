#!/usr/bin/env python
"""
Django Shell script để test các field types nâng cao
Chạy với: python manage.py shell < shell_test.py
"""

print("🚀 Django Shell - Testing Advanced Field Types")
print("=" * 50)

from blog.models import *
from shop.models import *
from datetime import date, datetime, time, timedelta
from decimal import Decimal
import uuid

# 1. Test AdvancedFieldExample với tất cả field types
print("\n1. Testing AdvancedFieldExample...")
advanced = AdvancedFieldExample.objects.create(
    title="Django Field Types Demo",
    description="Demonstration of all Django field types\nwith Vietnamese content\nMultiple lines supported",
    slug=f"django-field-types-demo-{uuid.uuid4().hex[:8]}",
    email="demo@example.com",
    website="https://www.djangoproject.com",
    integer_field=2024,
    float_field=3.14159265359,
    decimal_field=Decimal('999999.99'),
    is_active=True,
    priority=AdvancedFieldExample.Priority.HIGH,
    score=98,
    date_field=date(2024, 12, 25),
    datetime_field=datetime(2024, 12, 25, 10, 30, 0),
    time_field=time(14, 30, 0),
    duration_field=timedelta(days=7, hours=8, minutes=30),
    ip_address='192.168.1.100',
    json_data={
        'course': 'Chuyên đề Công nghệ',
        'semester': 'HK1 2024-2025',
        'topics': ['Django Models', 'Field Types', 'Database Design'],
        'instructor': {
            'name': 'Giảng viên',
            'email': 'gv@university.edu.vn'
        },
        'students': 50,
        'completed': True
    },
    binary_data=b'Django Binary Data Example - Du lieu nhi phan'
)

print(f"✓ Created AdvancedFieldExample: {advanced.id}")
print(f"  Title: {advanced.title}")
print(f"  Slug: {advanced.slug}")
print(f"  Email: {advanced.email}")
print(f"  Priority: {advanced.get_priority_display()}")
print(f"  Score: {advanced.score}")
print(f"  Decimal: {advanced.decimal_field}")
print(f"  Date: {advanced.date_field}")
print(f"  DateTime: {advanced.datetime_field}")
print(f"  Duration: {advanced.duration_field}")
print(f"  IP Address: {advanced.ip_address}")
print(f"  JSON Keys: {list(advanced.json_data.keys())}")

# 2. Test Product với constraints
print("\n2. Testing Product with constraints...")
product = Product.objects.create(
    name="MacBook Pro M3",
    sku=f"MBP-M3-2024-{uuid.uuid4().hex[:6]}",
    price=Decimal('45999000.00'),  # 45,999,000 VND
    is_available=True
)
print(f"✓ Created Product: {product.name}")
print(f"  SKU: {product.sku}")
print(f"  Price: {product.price:,} VND")
print(f"  Available: {product.is_available}")

# 3. Test Book-Author-Review relationships
print("\n3. Testing Book-Author-Review relationships...")

# Tạo authors
author1 = Author.objects.create(
    name="Dale Carnegie",
    email=f"dale{uuid.uuid4().hex[:6]}@example.com",
    birth_date=date(1888, 11, 24),
    bio="American writer and lecturer"
)

author2 = Author.objects.create(
    name="Napoleon Hill",
    email=f"napoleon{uuid.uuid4().hex[:6]}@example.com", 
    birth_date=date(1883, 10, 26),
    bio="American self-help author"
)

# Tạo book
book = Book.objects.create(
    title=f"How to Win Friends and Influence People {uuid.uuid4().hex[:6]}",
    isbn=f"978-0-671-{uuid.uuid4().hex[:8]}",
    publication_date=date(1936, 10, 1),
    pages=291,
    price=Decimal('199000.00'),
    is_published=True
)

# Gán authors (Many-to-Many)
book.authors.add(author1)

# Tạo reviews
review1 = Review.objects.create(
    book=book,
    reviewer_name="Student A",
    rating=5,
    comment="Excellent book for personal development!"
)

review2 = Review.objects.create(
    book=book,
    reviewer_name="Teacher B", 
    rating=4,
    comment="Great insights for communication skills."
)

print(f"✓ Created Book: {book.title}")
print(f"  Authors: {', '.join([str(a) for a in book.authors.all()])}")
print(f"  Reviews: {book.reviews.count()}")
avg_rating = sum(r.rating for r in book.reviews.all()) / book.reviews.count()
print(f"  Average Rating: {avg_rating:.1f}/5")

# 4. Test Many-to-Many với Pizza-Toppings
print("\n4. Testing Pizza-Toppings (Many-to-Many)...")

# Tạo toppings
cheese = Topping.objects.create(name="Mozzarella Cheese")
pepperoni = Topping.objects.create(name="Pepperoni")
mushroom = Topping.objects.create(name="Fresh Mushrooms")
olives = Topping.objects.create(name="Black Olives")

# Tạo pizza
pizza = Pizza.objects.create(name="Deluxe Supreme")
pizza.toppings.add(cheese, pepperoni, mushroom, olives)

print(f"✓ Created Pizza: {pizza.name}")
print(f"  Toppings: {', '.join([t.name for t in pizza.toppings.all()])}")

# 5. Test Shop models (Through model, Inheritance)
print("\n5. Testing Shop models...")

# Through model example
person = Person.objects.create(name="Nguyễn Văn Dev")
group = Group.objects.create(name="Django Developers")
membership = Membership.objects.create(
    person=person,
    group=group,
    date_joined=date.today(),
    invite_reason="Expert in Django field types"
)
print(f"✓ Membership: {person.name} joined {group.name}")

# Inheritance example
restaurant = Restaurant.objects.create(
    name="Phở Việt Nam",
    address="123 Nguyễn Huệ, Q1, TP.HCM",
    serves_hot_dogs=False,
    serves_pizza=False
)
print(f"✓ Restaurant: {restaurant.name}")

# ForeignKey example
toyota = Manufacturer.objects.create(name="Toyota Vietnam")
car = Car.objects.create(
    manufacturer=toyota,
    name="Vios 2024",
    year=2024
)
print(f"✓ Car: {car.manufacturer.name} {car.name}")

# 6. Thống kê cuối
print("\n" + "=" * 50)
print("📊 FINAL STATISTICS:")
print(f"  AdvancedFieldExample: {AdvancedFieldExample.objects.count()}")
print(f"  Product: {Product.objects.count()}")
print(f"  Author: {Author.objects.count()}")
print(f"  Book: {Book.objects.count()}")
print(f"  Review: {Review.objects.count()}")
print(f"  Pizza: {Pizza.objects.count()}")
print(f"  Topping: {Topping.objects.count()}")
print(f"  Restaurant: {Restaurant.objects.count()}")
print(f"  Car: {Car.objects.count()}")

print("\n✅ ALL FIELD TYPES TESTED SUCCESSFULLY!")
print("🎉 Django Models & Field Types demo completed!")
