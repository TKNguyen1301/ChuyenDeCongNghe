#!/usr/bin/env python
"""
Django Indexes Performance Testing Script
Test các loại indexes khác nhau và đo performance
"""
import os
import sys
import django
import time
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.append('/Users/nguyen/Downloads/ChuyenDeCongNghe/lab2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modelspractice.settings')
django.setup()

from django.db import connection
from django.db.models import Q, F, Count, Sum, Avg
from django.db.models.functions import Lower, Length
from indexes_practice.models import Article, Product, Customer, Order, LogEntry

def reset_query_count():
    """Reset query count để đo performance"""
    connection.queries_log.clear()

def get_query_count():
    """Lấy số lượng queries đã thực hiện"""
    return len(connection.queries_log)

def time_function(func):
    """Decorator để đo thời gian thực hiện"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        reset_query_count()
        result = func(*args, **kwargs)
        end_time = time.time()
        query_count = get_query_count()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"  ⏱️  {execution_time:.2f}ms | 🔍 {query_count} queries")
        return result
    return wrapper

def create_sample_data():
    """Tạo dữ liệu mẫu để test performance"""
    print("🚀 Creating sample data for performance testing...")
    
    # Create Articles
    print("Creating Articles...")
    categories = ['Technology', 'Science', 'Business', 'Health', 'Education']
    statuses = ['draft', 'published', 'archived']
    
    for i in range(1000):
        Article.objects.create(
            title=f"Article {i+1}: {random.choice(['Django', 'Python', 'Web Development', 'Database', 'Performance'])}",
            slug=f"article-{i+1}-{random.randint(1000, 9999)}",
            content=f"Content for article {i+1}. " * random.randint(50, 200),
            summary=f"Summary for article {i+1}",
            status=random.choice(statuses),
            category=random.choice(categories),
            view_count=random.randint(0, 10000),
            rating=Decimal(str(round(random.uniform(0, 5), 2))),
            word_count=random.randint(100, 2000),
            is_featured=random.choice([True, False]),
            is_premium=random.choice([True, False]),
            tags=f"tag{random.randint(1,10)},tag{random.randint(1,10)}"
        )
    print(f"✅ Created {Article.objects.count()} articles")
    
    # Create Customers
    print("Creating Customers...")
    countries = ['Vietnam', 'USA', 'UK', 'Japan', 'Australia']
    cities = ['Ho Chi Minh City', 'Hanoi', 'New York', 'London', 'Tokyo']
    tiers = ['bronze', 'silver', 'gold', 'platinum']
    
    for i in range(500):
        Customer.objects.create(
            first_name=f"Customer{i+1}",
            last_name=f"Test{i+1}",
            email=f"customer{i+1}@example.com",
            phone=f"0{random.randint(100000000, 999999999)}",
            city=random.choice(cities),
            country=random.choice(countries),
            postal_code=f"{random.randint(10000, 99999)}",
            is_active=random.choice([True, False]),
            is_vip=random.choice([True, False]),
            customer_tier=random.choice(tiers),
            total_orders=random.randint(0, 100),
            total_spent=Decimal(str(random.randint(0, 10000000))),  # 0-10M VND
            lifetime_value=Decimal(str(random.randint(0, 15000000)))  # 0-15M VND
        )
    print(f"✅ Created {Customer.objects.count()} customers")
    
    # Create Products
    print("Creating Products...")
    categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports']
    brands = ['Apple', 'Samsung', 'Nike', 'Adidas', 'Sony']
    
    for i in range(1000):
        Product.objects.create(
            name=f"Product {i+1}",
            sku=f"PRD-{i+1:04d}-{random.randint(1000, 9999)}",
            barcode=f"{random.randint(1000000000000, 9999999999999)}",
            price=Decimal(str(random.randint(10000, 5000000))),  # 10K-5M VND
            cost=Decimal(str(random.randint(5000, 2500000))),    # 5K-2.5M VND
            discount_percentage=Decimal(str(random.randint(0, 50))),
            stock_quantity=random.randint(0, 1000),
            is_active=random.choice([True, False]),
            is_digital=random.choice([True, False]),
            category=random.choice(categories),
            subcategory=f"Sub{random.choice(categories)}",
            brand=random.choice(brands),
            sales_count=random.randint(0, 1000),
            views_count=random.randint(0, 10000)
        )
    print(f"✅ Created {Product.objects.count()} products")
    
    # Create Orders
    print("Creating Orders...")
    customers = list(Customer.objects.all())
    statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    
    for i in range(2000):
        customer = random.choice(customers)
        total = Decimal(str(random.randint(50000, 2000000)))  # 50K-2M VND
        Order.objects.create(
            customer=customer,
            order_number=f"ORD-{i+1:06d}",
            status=random.choice(statuses),
            subtotal=total * Decimal('0.9'),
            tax_amount=total * Decimal('0.1'),
            shipping_cost=Decimal(str(random.randint(0, 50000))),
            discount_amount=Decimal(str(random.randint(0, 100000))),
            total_amount=total,
            shipping_method=random.choice(['standard', 'express', 'overnight']),
            tracking_number=f"TRK{random.randint(1000000000, 9999999999)}" if random.choice([True, False]) else "",
            items_count=random.randint(1, 10)
        )
    print(f"✅ Created {Order.objects.count()} orders")
    
    # Create Log Entries
    print("Creating Log Entries...")
    levels = ['debug', 'info', 'warning', 'error', 'critical']
    modules = ['auth', 'orders', 'products', 'payments', 'shipping']
    
    for i in range(5000):
        LogEntry.objects.create(
            level=random.choice(levels),
            message=f"Log message {i+1}: {random.choice(['User action', 'System event', 'Error occurred', 'Info message'])}",
            module=random.choice(modules),
            function=f"function_{random.randint(1, 100)}",
            user_id=random.randint(1, 100) if random.choice([True, False]) else None,
            ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            request_path=f"/api/{random.choice(modules)}/{random.randint(1, 1000)}",
            duration_ms=random.randint(1, 5000),
            extra_data={'key': f'value_{i+1}', 'count': random.randint(1, 100)}
        )
    print(f"✅ Created {LogEntry.objects.count()} log entries")
    
    print("\n🎉 Sample data creation completed!")

def test_article_queries():
    """Test performance của Article queries với indexes"""
    print("\n📰 TESTING ARTICLE QUERIES")
    print("=" * 50)
    
    @time_function
    def test_simple_filter():
        """Test simple field index"""
        return list(Article.objects.filter(status='published')[:100])
    
    @time_function
    def test_composite_filter():
        """Test composite index"""
        return list(Article.objects.filter(status='published', category='Technology')[:100])
    
    @time_function
    def test_partial_index():
        """Test partial index - chỉ published articles"""
        return list(Article.objects.filter(status='published', rating__gte=4.0)[:100])
    
    @time_function
    def test_functional_index():
        """Test functional index - Lower title"""
        return list(Article.objects.filter(title__icontains='django')[:100])
    
    @time_function
    def test_complex_query():
        """Test complex query với nhiều conditions"""
        return list(Article.objects.filter(
            Q(status='published') & 
            Q(category='Technology') & 
            Q(view_count__gt=1000) & 
            Q(is_featured=True)
        )[:50])
    
    print("1. Simple status filter (indexed):")
    test_simple_filter()
    
    print("2. Composite filter (status + category):")
    test_composite_filter()
    
    print("3. Partial index query (high rating published):")
    test_partial_index()
    
    print("4. Functional index query (case-insensitive title):")
    test_functional_index()
    
    print("5. Complex multi-condition query:")
    test_complex_query()

def test_product_queries():
    """Test performance của Product queries"""
    print("\n🛍️  TESTING PRODUCT QUERIES")
    print("=" * 50)
    
    @time_function
    def test_ecommerce_filter():
        """Test e-commerce typical query"""
        return list(Product.objects.filter(
            is_active=True,
            stock_quantity__gt=0,
            category='Electronics'
        ).order_by('-sales_count')[:50])
    
    @time_function
    def test_price_range():
        """Test price range query"""
        return list(Product.objects.filter(
            price__gte=100000,  # >= 100K VND
            price__lte=1000000  # <= 1M VND
        )[:100])
    
    @time_function
    def test_bestsellers():
        """Test bestsellers query với partial index"""
        return list(Product.objects.filter(sales_count__gte=100)[:50])
    
    @time_function
    def test_brand_category():
        """Test brand + category composite index"""
        return list(Product.objects.filter(
            brand='Apple',
            category='Electronics'
        ).order_by('-created_at')[:50])
    
    print("1. E-commerce filter (active + in stock + category):")
    test_ecommerce_filter()
    
    print("2. Price range filter:")
    test_price_range()
    
    print("3. Bestsellers query (partial index):")
    test_bestsellers()
    
    print("4. Brand + Category filter:")
    test_brand_category()

def test_customer_analytics():
    """Test Customer analytics queries"""
    print("\n👥 TESTING CUSTOMER ANALYTICS")
    print("=" * 50)
    
    @time_function
    def test_vip_customers():
        """Test VIP customers query"""
        return list(Customer.objects.filter(is_vip=True)[:100])
    
    @time_function
    def test_high_value_customers():
        """Test high-value customers với partial index"""
        return list(Customer.objects.filter(lifetime_value__gte=1000000)[:50])
    
    @time_function
    def test_customer_segmentation():
        """Test customer segmentation"""
        return list(Customer.objects.filter(
            customer_tier='platinum',
            is_active=True
        ).order_by('-total_spent')[:20])
    
    @time_function
    def test_geographic_analysis():
        """Test geographic analysis"""
        return list(Customer.objects.filter(
            country='Vietnam',
            total_orders__gte=5
        )[:100])
    
    print("1. VIP customers query:")
    test_vip_customers()
    
    print("2. High-value customers (partial index):")
    test_high_value_customers()
    
    print("3. Customer segmentation (tier + active):")
    test_customer_segmentation()
    
    print("4. Geographic analysis:")
    test_geographic_analysis()

def test_order_reporting():
    """Test Order reporting queries"""
    print("\n📊 TESTING ORDER REPORTING")
    print("=" * 50)
    
    @time_function
    def test_recent_orders():
        """Test recent orders"""
        return list(Order.objects.order_by('-created_at')[:100])
    
    @time_function
    def test_order_status():
        """Test orders by status"""
        return list(Order.objects.filter(status='delivered')[:100])
    
    @time_function
    def test_customer_orders():
        """Test customer orders"""
        customer = Customer.objects.first()
        return list(Order.objects.filter(customer=customer).order_by('-created_at')[:50])
    
    @time_function
    def test_high_value_orders():
        """Test high-value orders"""
        return list(Order.objects.filter(total_amount__gte=1000000)[:50])
    
    print("1. Recent orders (time-based index):")
    test_recent_orders()
    
    print("2. Orders by status:")
    test_order_status()
    
    print("3. Customer orders:")
    test_customer_orders()
    
    print("4. High-value orders:")
    test_high_value_orders()

def test_log_monitoring():
    """Test Log monitoring queries"""
    print("\n📋 TESTING LOG MONITORING")
    print("=" * 50)
    
    @time_function
    def test_error_logs():
        """Test error logs với partial index"""
        return list(LogEntry.objects.filter(level__in=['error', 'critical'])[:100])
    
    @time_function
    def test_recent_logs():
        """Test recent logs"""
        return list(LogEntry.objects.order_by('-timestamp')[:100])
    
    @time_function
    def test_module_logs():
        """Test logs by module"""
        return list(LogEntry.objects.filter(module='orders')[:100])
    
    @time_function
    def test_slow_requests():
        """Test slow requests với partial index"""
        return list(LogEntry.objects.filter(duration_ms__gte=1000)[:50])
    
    print("1. Error logs (partial index):")
    test_error_logs()
    
    print("2. Recent logs (time-based):")
    test_recent_logs()
    
    print("3. Module-specific logs:")
    test_module_logs()
    
    print("4. Slow requests (performance analysis):")
    test_slow_requests()

def test_aggregation_queries():
    """Test aggregation queries với indexes"""
    print("\n📈 TESTING AGGREGATION QUERIES")
    print("=" * 50)
    
    @time_function
    def test_article_stats():
        """Test article statistics"""
        return Article.objects.aggregate(
            total_views=Sum('view_count'),
            avg_rating=Avg('rating'),
            published_count=Count('id', filter=Q(status='published'))
        )
    
    @time_function
    def test_customer_analytics():
        """Test customer analytics"""
        return Customer.objects.aggregate(
            total_customers=Count('id'),
            total_revenue=Sum('total_spent'),
            avg_lifetime_value=Avg('lifetime_value'),
            vip_count=Count('id', filter=Q(is_vip=True))
        )
    
    @time_function
    def test_order_analytics():
        """Test order analytics"""
        return Order.objects.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total_amount'),
            avg_order_value=Avg('total_amount'),
            delivered_count=Count('id', filter=Q(status='delivered'))
        )
    
    print("1. Article statistics:")
    result = test_article_stats()
    print(f"   📊 {result}")
    
    print("2. Customer analytics:")
    result = test_customer_analytics()
    print(f"   📊 {result}")
    
    print("3. Order analytics:")
    result = test_order_analytics()
    print(f"   📊 {result}")

def show_indexes_summary():
    """Hiển thị tổng kết về indexes đã tạo"""
    print("\n📋 INDEXES SUMMARY")
    print("=" * 60)
    
    models_info = [
        ('Article', Article._meta.indexes, Article.objects.count()),
        ('Product', Product._meta.indexes, Product.objects.count()),
        ('Customer', Customer._meta.indexes, Customer.objects.count()),
        ('Order', Order._meta.indexes, Order.objects.count()),
        ('LogEntry', LogEntry._meta.indexes, LogEntry.objects.count()),
    ]
    
    total_indexes = 0
    for model_name, indexes, count in models_info:
        print(f"\n🏷️  {model_name} ({count} records)")
        print(f"   📊 {len(indexes)} indexes:")
        for idx in indexes:
            index_type = "Functional" if idx.expressions else "Field-based"
            if idx.condition:
                index_type += " + Partial"
            if hasattr(idx, 'include') and idx.include:
                index_type += " + Covering"
            print(f"   • {idx.name or 'auto'} ({index_type})")
        total_indexes += len(indexes)
    
    print(f"\n🎯 TOTAL: {total_indexes} indexes across {len(models_info)} models")
    
    print("\n📚 INDEX TYPES DEMONSTRATED:")
    print("• Simple B-Tree indexes (single field)")
    print("• Composite indexes (multiple fields)")
    print("• Partial indexes (with WHERE conditions)")
    print("• Functional indexes (on expressions)")
    print("• Covering indexes (with INCLUDE - PostgreSQL)")
    print("• Descending order indexes")

def run_performance_tests():
    """Chạy tất cả performance tests"""
    print("🚀 DJANGO INDEXES PERFORMANCE TESTING")
    print("=" * 60)
    print("Testing database performance with various index types")
    print(f"Database Engine: {connection.vendor}")
    print("=" * 60)
    
    # Đếm dữ liệu hiện tại
    counts = {
        'Article': Article.objects.count(),
        'Product': Product.objects.count(),
        'Customer': Customer.objects.count(),
        'Order': Order.objects.count(),
        'LogEntry': LogEntry.objects.count(),
    }
    
    print(f"📊 Current data counts: {counts}")
    
    # Nếu chưa có đủ dữ liệu, tạo sample data
    if any(count < 100 for count in counts.values()):
        create_sample_data()
    
    # Chạy các tests
    test_article_queries()
    test_product_queries()
    test_customer_analytics()
    test_order_reporting()
    test_log_monitoring()
    test_aggregation_queries()
    
    # Hiển thị summary
    show_indexes_summary()
    
    print("\n🎉 PERFORMANCE TESTING COMPLETED!")
    print("💡 Indexes significantly improve query performance!")
    print("📈 Lower execution times indicate better index utilization")

if __name__ == '__main__':
    run_performance_tests()
