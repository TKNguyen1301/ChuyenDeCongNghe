#!/usr/bin/env python
"""
Database Schema Inspector for Meta Options
Shows how Meta options affect actual database structure
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modelspractice.settings')
django.setup()

from django.db import connection
from django.apps import apps


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*70}")
    print(f"🔍 {title}")
    print(f"{'='*70}")


def print_section(title):
    """Print a formatted section."""
    print(f"\n{'─'*50}")
    print(f"📊 {title}")
    print(f"{'─'*50}")


def inspect_database_tables():
    """Inspect actual database tables created by Meta options."""
    print_header("DATABASE TABLES CREATED BY META OPTIONS")
    
    with connection.cursor() as cursor:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        all_tables = [row[0] for row in cursor.fetchall()]
        
        # Filter meta_practice tables
        meta_tables = [table for table in all_tables if 'meta_practice' in table or 'custom_blog' in table or 'complete_example' in table]
        
        print("🗄️  Tables created by meta_practice app:")
        for table in meta_tables:
            print(f"   📋 {table}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            
            print(f"      Columns:")
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                not_null = "NOT NULL" if col[3] else "NULL"
                default = f"DEFAULT {col[4]}" if col[4] else ""
                pk = "PRIMARY KEY" if col[5] else ""
                print(f"        - {col_name}: {col_type} {not_null} {default} {pk}".strip())


def inspect_indexes():
    """Inspect indexes created by Meta options."""
    print_header("INDEXES CREATED BY META OPTIONS")
    
    with connection.cursor() as cursor:
        # Get all indexes for meta_practice tables
        cursor.execute("""
            SELECT name, tbl_name, sql 
            FROM sqlite_master 
            WHERE type='index' 
            AND (tbl_name LIKE '%meta_practice%' OR tbl_name LIKE '%custom_blog%' OR tbl_name LIKE '%complete_example%')
            AND name NOT LIKE 'sqlite_%'
            ORDER BY tbl_name, name;
        """)
        
        indexes = cursor.fetchall()
        
        current_table = None
        for index in indexes:
            index_name, table_name, sql = index
            
            if table_name != current_table:
                print_section(f"Table: {table_name}")
                current_table = table_name
            
            print(f"   📈 Index: {index_name}")
            if sql:
                # Extract fields from CREATE INDEX statement
                if "ON" in sql:
                    fields_part = sql.split("ON")[1].split("(")[1].split(")")[0]
                    print(f"      Fields: {fields_part}")
                    
                # Check for partial index
                if "WHERE" in sql:
                    condition = sql.split("WHERE")[1].strip()
                    print(f"      Condition: {condition}")


def inspect_constraints():
    """Inspect constraints created by Meta options."""
    print_header("CONSTRAINTS CREATED BY META OPTIONS")
    
    with connection.cursor() as cursor:
        # Get constraints for meta_practice tables
        meta_tables = []
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%meta_practice%' OR name LIKE '%custom_blog%' OR name LIKE '%complete_example%');")
        meta_tables = [row[0] for row in cursor.fetchall()]
        
        for table in meta_tables:
            print_section(f"Table: {table}")
            
            # Get table SQL to see constraints
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}';")
            table_sql = cursor.fetchone()[0]
            
            # Parse constraints from CREATE TABLE statement
            if "CHECK" in table_sql:
                print("   🔒 Check Constraints found in table definition")
                # Extract CHECK constraints
                lines = table_sql.split('\n')
                for line in lines:
                    if 'CHECK' in line and 'CONSTRAINT' in line:
                        constraint_name = line.split('CONSTRAINT')[1].split('CHECK')[0].strip().strip('"')
                        check_condition = line.split('CHECK')[1].strip().rstrip(',').strip('()')
                        print(f"      - {constraint_name}: CHECK {check_condition}")
            
            if "UNIQUE" in table_sql:
                print("   🔑 Unique Constraints found in table definition")
                lines = table_sql.split('\n')
                for line in lines:
                    if 'UNIQUE' in line and 'CONSTRAINT' in line:
                        constraint_name = line.split('CONSTRAINT')[1].split('UNIQUE')[0].strip().strip('"')
                        unique_fields = line.split('UNIQUE')[1].strip().rstrip(',').strip('()')
                        print(f"      - {constraint_name}: UNIQUE {unique_fields}")


def inspect_permissions():
    """Inspect custom permissions created by Meta options."""
    print_header("CUSTOM PERMISSIONS CREATED BY META OPTIONS")
    
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import Permission
    
    # Get meta_practice app models
    app = apps.get_app_config('meta_practice')
    models = app.get_models()
    
    for model in models:
        if not model._meta.proxy and model._meta.managed:
            print_section(f"Model: {model.__name__}")
            
            content_type = ContentType.objects.get_for_model(model)
            permissions = Permission.objects.filter(content_type=content_type).order_by('codename')
            
            # Separate default and custom permissions
            default_perms = ['add', 'change', 'delete', 'view']
            custom_perms = []
            default_perms_found = []
            
            for perm in permissions:
                is_default = any(perm.codename.startswith(default) for default in default_perms)
                if is_default:
                    default_perms_found.append(perm)
                else:
                    custom_perms.append(perm)
            
            print("   🔐 Default Permissions:")
            for perm in default_perms_found:
                print(f"      - {perm.codename}: {perm.name}")
            
            if custom_perms:
                print("   🔒 Custom Permissions:")
                for perm in custom_perms:
                    print(f"      - {perm.codename}: {perm.name}")
            else:
                print("   ℹ️  No custom permissions defined")


def inspect_meta_configuration():
    """Inspect Meta configuration for each model."""
    print_header("META CONFIGURATION SUMMARY")
    
    app = apps.get_app_config('meta_practice')
    models = app.get_models()
    
    for model in models:
        print_section(f"Model: {model.__name__}")
        meta = model._meta
        
        # Basic info
        print(f"   📦 Model: {meta.model_name}")
        print(f"   🗄️  Table: {meta.db_table}")
        print(f"   📝 Verbose: {meta.verbose_name} / {meta.verbose_name_plural}")
        
        # Type info
        model_type = []
        if meta.abstract:
            model_type.append("Abstract")
        if meta.proxy:
            model_type.append("Proxy")
        if not meta.managed:
            model_type.append("Unmanaged")
        if not model_type:
            model_type.append("Regular")
        print(f"   🔧 Type: {', '.join(model_type)}")
        
        # Ordering
        if meta.ordering:
            print(f"   📊 Ordering: {meta.ordering}")
        
        # Get latest by
        if meta.get_latest_by:
            print(f"   ⏰ Latest By: {meta.get_latest_by}")
        
        # Indexes count
        if hasattr(meta, 'indexes') and meta.indexes:
            print(f"   📈 Indexes: {len(meta.indexes)} defined")
        
        # Constraints count
        if hasattr(meta, 'constraints') and meta.constraints:
            print(f"   🔒 Constraints: {len(meta.constraints)} defined")
        
        # Permissions count
        if hasattr(meta, 'permissions') and meta.permissions:
            print(f"   🔐 Custom Permissions: {len(meta.permissions)} defined")


def analyze_meta_options_impact():
    """Analyze the impact of Meta options on the application."""
    print_header("META OPTIONS IMPACT ANALYSIS")
    
    print_section("Database Optimization Impact")
    
    with connection.cursor() as cursor:
        # Count total indexes
        cursor.execute("""
            SELECT COUNT(*) 
            FROM sqlite_master 
            WHERE type='index' 
            AND (tbl_name LIKE '%meta_practice%' OR tbl_name LIKE '%custom_blog%' OR tbl_name LIKE '%complete_example%')
            AND name NOT LIKE 'sqlite_%';
        """)
        total_indexes = cursor.fetchone()[0]
        print(f"   📈 Total Indexes Created: {total_indexes}")
        
        # Count tables with custom names
        cursor.execute("""
            SELECT COUNT(*) 
            FROM sqlite_master 
            WHERE type='table' 
            AND (name = 'custom_blog_posts' OR name = 'complete_example');
        """)
        custom_tables = cursor.fetchone()[0]
        print(f"   🗄️  Tables with Custom Names: {custom_tables}")
    
    print_section("Permission System Impact")
    from django.contrib.auth.models import Permission
    
    # Count custom permissions
    custom_perms = Permission.objects.filter(
        content_type__app_label='meta_practice'
    ).exclude(
        codename__startswith='add_'
    ).exclude(
        codename__startswith='change_'
    ).exclude(
        codename__startswith='delete_'
    ).exclude(
        codename__startswith='view_'
    ).count()
    
    print(f"   🔐 Custom Permissions Created: {custom_perms}")
    
    print_section("Model Inheritance Impact")
    
    # Count models by type
    app = apps.get_app_config('meta_practice')
    models = app.get_models()
    
    abstract_count = sum(1 for model in models if model._meta.abstract)
    proxy_count = sum(1 for model in models if model._meta.proxy)
    unmanaged_count = sum(1 for model in models if not model._meta.managed)
    regular_count = len(models) - abstract_count - proxy_count - unmanaged_count
    
    print(f"   🏗️  Abstract Models: {abstract_count}")
    print(f"   🔄 Proxy Models: {proxy_count}")
    print(f"   ⚙️  Unmanaged Models: {unmanaged_count}")
    print(f"   📦 Regular Models: {regular_count}")


def run_inspection():
    """Run complete database schema inspection."""
    print("🔍 Starting Database Schema Inspection for Meta Options")
    
    inspection_functions = [
        inspect_meta_configuration,
        inspect_database_tables,
        inspect_indexes,
        inspect_constraints,
        inspect_permissions,
        analyze_meta_options_impact,
    ]
    
    for func in inspection_functions:
        try:
            func()
        except Exception as e:
            print(f"❌ Error in {func.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print_header("INSPECTION COMPLETED")
    print("🎉 Database schema inspection finished!")
    print("💡 This shows how Django Meta options directly affect database structure!")


if __name__ == "__main__":
    run_inspection()
