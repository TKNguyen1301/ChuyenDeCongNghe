#!/usr/bin/env python
"""
Django Database Indexes Inspection Script
Kiểm tra và phân tích indexes trong database
"""
import os
import sys
import django

# Setup Django
sys.path.append('/Users/nguyen/Downloads/ChuyenDeCongNghe/lab2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modelspractice.settings')
django.setup()

from django.db import connection
from django.apps import apps
from indexes_practice.models import Article, Product, Customer, Order, LogEntry

def get_database_info():
    """Lấy thông tin database"""
    print("🗄️  DATABASE INFORMATION")
    print("=" * 50)
    print(f"Database Engine: {connection.vendor}")
    print(f"Database Name: {connection.settings_dict.get('NAME', 'N/A')}")
    print(f"Django Version: {django.get_version()}")
    print()

def show_model_indexes():
    """Hiển thị tất cả indexes của models"""
    print("📋 MODEL INDEXES ANALYSIS")
    print("=" * 50)
    
    models = [Article, Product, Customer, Order, LogEntry]
    
    for model in models:
        print(f"\n🏷️  {model.__name__}")
        print(f"📊 Table: {model._meta.db_table}")
        print(f"📈 Records: {model.objects.count():,}")
        
        indexes = model._meta.indexes
        print(f"🔍 Defined Indexes: {len(indexes)}")
        
        for i, index in enumerate(indexes, 1):
            print(f"\n   {i}. {index.name or f'auto_{i}'}")
            
            # Index type analysis
            index_types = []
            if index.expressions:
                index_types.append("Functional")
                print(f"      Expressions: {[str(expr) for expr in index.expressions]}")
            if index.fields:
                index_types.append("Field-based")
                print(f"      Fields: {list(index.fields)}")
            if index.condition:
                index_types.append("Partial")
                print(f"      Condition: {index.condition}")
            if hasattr(index, 'include') and index.include:
                index_types.append("Covering")
                print(f"      Include: {list(index.include)}")
            
            print(f"      Type: {' + '.join(index_types)}")
        
        print("-" * 40)

def analyze_database_indexes():
    """Phân tích indexes thực tế trong database"""
    print("\n🔍 DATABASE INDEXES ANALYSIS")
    print("=" * 50)
    
    with connection.cursor() as cursor:
        if connection.vendor == 'sqlite':
            # SQLite: Lấy danh sách indexes
            cursor.execute("""
                SELECT name, tbl_name, sql 
                FROM sqlite_master 
                WHERE type = 'index' 
                AND name NOT LIKE 'sqlite_%'
                AND tbl_name LIKE 'indexes_practice_%'
                ORDER BY tbl_name, name
            """)
            
            indexes = cursor.fetchall()
            
            if indexes:
                current_table = ""
                for index_name, table_name, sql in indexes:
                    if table_name != current_table:
                        print(f"\n📊 Table: {table_name}")
                        current_table = table_name
                    
                    print(f"   • {index_name}")
                    if sql:
                        # Rút gọn SQL để dễ đọc
                        sql_short = sql.replace('CREATE INDEX', '').replace(table_name, '').strip()
                        if len(sql_short) > 80:
                            sql_short = sql_short[:80] + "..."
                        print(f"     SQL: {sql_short}")
            else:
                print("❌ No custom indexes found")
                
        elif connection.vendor == 'postgresql':
            # PostgreSQL: Thông tin chi tiết hơn
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE tablename LIKE 'indexes_practice_%'
                ORDER BY tablename, indexname
            """)
            
            indexes = cursor.fetchall()
            for schema, table, index_name, index_def in indexes:
                print(f"📊 {table}")
                print(f"   • {index_name}")
                print(f"     Definition: {index_def}")
                print()

def show_query_performance_tips():
    """Hiển thị tips về query performance"""
    print("\n💡 QUERY PERFORMANCE TIPS")
    print("=" * 50)
    
    tips = [
        "1. 🎯 Sử dụng .select_related() cho ForeignKey để tránh N+1 queries",
        "2. 🔄 Sử dụng .prefetch_related() cho ManyToMany và reverse ForeignKey",
        "3. 📊 Sử dụng .only() và .defer() để chỉ load fields cần thiết",
        "4. 🎭 Sử dụng .exists() thay vì len() để check existence",
        "5. 📈 Sử dụng .count() thay vì len() để đếm records",
        "6. 🔍 Filter trong database thay vì Python (WHERE vs Python filtering)",
        "7. 📊 Sử dụng aggregation functions trong database",
        "8. 🎯 Tạo indexes cho fields thường xuyên filter/order",
        "9. 🔄 Sử dụng bulk operations cho mass INSERT/UPDATE",
        "10. 📋 Monitor slow queries bằng Django Debug Toolbar",
    ]
    
    for tip in tips:
        print(f"   {tip}")

def demonstrate_index_usage():
    """Demonstrate cách indexes được sử dụng"""
    print("\n🚀 INDEX USAGE DEMONSTRATION")
    print("=" * 50)
    
    # Enable query logging
    connection.force_debug_cursor = True
    
    examples = [
        {
            'name': 'Simple Index Usage',
            'query': lambda: list(Article.objects.filter(status='published')[:5]),
            'note': 'Uses status index'
        },
        {
            'name': 'Composite Index Usage', 
            'query': lambda: list(Article.objects.filter(status='published', category='Technology')[:5]),
            'note': 'Uses composite status+category index'
        },
        {
            'name': 'Partial Index Usage',
            'query': lambda: list(Article.objects.filter(status='published', rating__gte=4.0)[:5]),
            'note': 'Uses partial index for high-rating published articles'
        },
        {
            'name': 'Order By Index Usage',
            'query': lambda: list(Article.objects.filter(category='Technology').order_by('-created_at')[:5]),
            'note': 'Uses category+created_at descending index'
        }
    ]
    
    for example in examples:
        print(f"\n📝 {example['name']}")
        print(f"   💡 {example['note']}")
        
        # Clear previous queries
        connection.queries_log.clear()
        
        # Execute query
        try:
            result = example['query']()
            query_count = len(connection.queries_log)
            
            if connection.queries_log:
                sql = connection.queries_log[-1]['sql']
                # Rút gọn SQL cho dễ đọc
                sql_parts = sql.split()
                if len(sql_parts) > 15:
                    sql_short = ' '.join(sql_parts[:15]) + " ..."
                else:
                    sql_short = sql
                print(f"   🔍 SQL: {sql_short}")
            
            print(f"   📊 Results: {len(result)} records, {query_count} queries")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

def check_index_coverage():
    """Kiểm tra index coverage cho common queries"""
    print("\n📊 INDEX COVERAGE ANALYSIS")
    print("=" * 50)
    
    coverage_tests = [
        {
            'model': 'Article',
            'queries': [
                'status = published',
                'category = Technology', 
                'status = published AND category = Technology',
                'view_count > 1000',
                'rating >= 4.0 AND status = published'
            ]
        },
        {
            'model': 'Product',
            'queries': [
                'is_active = True',
                'category = Electronics',
                'price BETWEEN 100K AND 1M',
                'is_active = True AND stock_quantity > 0'
            ]
        },
        {
            'model': 'Order',
            'queries': [
                'status = delivered',
                'created_at > last_month',
                'customer_id = X AND status = pending',
                'total_amount > 1M'
            ]
        }
    ]
    
    for test in coverage_tests:
        print(f"\n🏷️  {test['model']} Query Patterns:")
        for query in test['queries']:
            # Đánh giá khả năng có index phù hợp
            has_likely_index = "✅" if any(keyword in query.lower() for keyword in ['status', 'category', 'is_active', 'created_at']) else "⚠️"
            print(f"   {has_likely_index} {query}")

def main():
    """Main function chạy tất cả analyses"""
    print("🔍 DJANGO INDEXES INSPECTION TOOL")
    print("=" * 60)
    
    get_database_info()
    show_model_indexes()
    analyze_database_indexes() 
    demonstrate_index_usage()
    check_index_coverage()
    show_query_performance_tips()
    
    print("\n" + "=" * 60)
    print("✅ Inspection completed!")
    print("💡 Use this information to optimize your database queries")

if __name__ == '__main__':
    main()
