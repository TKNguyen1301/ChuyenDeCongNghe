"""
Django Migration Operations - Complete Practice Examples
=========================================================

This file demonstrates all major Django migration operations with practical examples.
Run this file using: python manage.py shell < migration_operations_practice.py
"""

from django.db import migrations, models, connection
from django.db.migrations.operations import *
from django.apps import apps
import django.db.models.deletion


def demonstrate_migration_operations():
    """
    Demonstrates how migration operations work
    """
    print("=== DJANGO MIGRATION OPERATIONS PRACTICE ===\n")
    
    # 1. Schema Operations Examples
    print("1. SCHEMA OPERATIONS")
    print("-" * 50)
    
    # CreateModel Operation
    create_model_op = CreateModel(
        name='Product',
        fields=[
            ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('name', models.CharField(max_length=200)),
            ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
        ],
        options={
            'verbose_name': 'Product',
            'verbose_name_plural': 'Products',
            'ordering': ['name'],
        },
    )
    print(f"CreateModel: {create_model_op.describe()}")
    
    # AddField Operation
    add_field_op = AddField(
        model_name='Product',
        name='description',
        field=models.TextField(blank=True, null=True),
    )
    print(f"AddField: {add_field_op.describe()}")
    
    # AlterField Operation
    alter_field_op = AlterField(
        model_name='Product',
        name='price',
        field=models.DecimalField(decimal_places=2, max_digits=12, help_text='Price in USD'),
    )
    print(f"AlterField: {alter_field_op.describe()}")
    
    # RenameField Operation
    rename_field_op = RenameField(
        model_name='Product',
        old_name='created_at',
        new_name='date_created',
    )
    print(f"RenameField: {rename_field_op.describe()}")
    
    # RemoveField Operation
    remove_field_op = RemoveField(
        model_name='Product',
        name='description',
    )
    print(f"RemoveField: {remove_field_op.describe()}")
    
    # AddIndex Operation
    add_index_op = AddIndex(
        model_name='Product',
        index=models.Index(fields=['name', 'price'], name='product_name_price_idx'),
    )
    print(f"AddIndex: {add_index_op.describe()}")
    
    # AddConstraint Operation
    add_constraint_op = AddConstraint(
        model_name='Product',
        constraint=models.CheckConstraint(
            check=models.Q(price__gte=0),
            name='product_price_positive'
        ),
    )
    print(f"AddConstraint: {add_constraint_op.describe()}")
    
    print("\n2. SPECIAL OPERATIONS")
    print("-" * 50)
    
    # RunSQL Operation
    run_sql_op = RunSQL(
        sql="CREATE INDEX CONCURRENTLY IF NOT EXISTS product_name_gin ON model_class_practice_product USING gin(to_tsvector('english', name));",
        reverse_sql="DROP INDEX IF EXISTS product_name_gin;",
    )
    print(f"RunSQL: Custom SQL execution")
    
    # RunPython Operation - với forward và reverse functions
    def create_sample_data(apps, schema_editor):
        """Forward function for RunPython"""
        Product = apps.get_model('model_class_practice', 'Product')
        db_alias = schema_editor.connection.alias
        Product.objects.using(db_alias).bulk_create([
            Product(name='Laptop', price=999.99),
            Product(name='Mouse', price=29.99),
            Product(name='Keyboard', price=79.99),
        ])
    
    def remove_sample_data(apps, schema_editor):
        """Reverse function for RunPython"""
        Product = apps.get_model('model_class_practice', 'Product')
        db_alias = schema_editor.connection.alias
        Product.objects.using(db_alias).filter(
            name__in=['Laptop', 'Mouse', 'Keyboard']
        ).delete()
    
    run_python_op = RunPython(
        code=create_sample_data,
        reverse_code=remove_sample_data,
    )
    print(f"RunPython: Executes Python code in migration context")
    
    print("\n3. MODEL OPERATIONS")
    print("-" * 50)
    
    # RenameModel Operation
    rename_model_op = RenameModel(
        old_name='Product',
        new_name='Item',
    )
    print(f"RenameModel: {rename_model_op.describe()}")
    
    # AlterModelTable Operation
    alter_table_op = AlterModelTable(
        name='Product',
        table='custom_products_table',
    )
    print(f"AlterModelTable: {alter_table_op.describe()}")
    
    # AlterModelOptions Operation
    alter_options_op = AlterModelOptions(
        name='Product',
        options={
            'verbose_name': 'Store Product',
            'verbose_name_plural': 'Store Products',
            'ordering': ['-date_created'],
            'permissions': [
                ('can_view_reports', 'Can view product reports'),
            ],
        },
    )
    print(f"AlterModelOptions: {alter_options_op.describe()}")
    
    # DeleteModel Operation
    delete_model_op = DeleteModel(name='Product')
    print(f"DeleteModel: {delete_model_op.describe()}")
    
    print("\n4. ADVANCED OPERATIONS")
    print("-" * 50)
    
    # SeparateDatabaseAndState Operation
    separate_op = SeparateDatabaseAndState(
        database_operations=[
            RunSQL("ALTER TABLE model_class_practice_product ADD COLUMN temp_col VARCHAR(50);"),
        ],
        state_operations=[
            AddField(
                model_name='Product',
                name='temp_col',
                field=models.CharField(max_length=50, null=True),
            ),
        ],
    )
    print("SeparateDatabaseAndState: Separates database changes from Django state")
    
    print("\n5. OPERATION CATEGORIES AND SYMBOLS")
    print("-" * 50)
    from django.db.migrations.operations.base import OperationCategory
    
    categories = {
        OperationCategory.ADDITION: "+",
        OperationCategory.REMOVAL: "-", 
        OperationCategory.ALTERATION: "~",
        OperationCategory.PYTHON: "p",
        OperationCategory.SQL: "s",
        OperationCategory.MIXED: "?",
    }
    
    for category, symbol in categories.items():
        print(f"{symbol} - {category}")


def show_migration_file_example():
    """
    Shows a complete migration file example
    """
    print("\n" + "="*60)
    print("COMPLETE MIGRATION FILE EXAMPLE")
    print("="*60)
    
    migration_example = '''
# Generated migration file example
from django.db import migrations, models
import django.db.models.deletion


def populate_initial_data(apps, schema_editor):
    """Add some initial data"""
    Category = apps.get_model('myapp', 'Category')
    db_alias = schema_editor.connection.alias
    Category.objects.using(db_alias).bulk_create([
        Category(name='Electronics'),
        Category(name='Books'),
        Category(name='Clothing'),
    ])


def remove_initial_data(apps, schema_editor):
    """Remove initial data"""
    Category = apps.get_model('myapp', 'Category')
    db_alias = schema_editor.connection.alias
    Category.objects.using(db_alias).filter(
        name__in=['Electronics', 'Books', 'Clothing']
    ).delete()


class Migration(migrations.Migration):
    
    dependencies = [
        ('myapp', '0001_initial'),
    ]
    
    operations = [
        # 1. Create new model
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        
        # 2. Add field to existing model
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='myapp.category'
            ),
        ),
        
        # 3. Add index for performance
        migrations.AddIndex(
            model_name='product',
            index=models.Index(
                fields=['category', 'created_at'],
                name='product_cat_created_idx'
            ),
        ),
        
        # 4. Add constraint
        migrations.AddConstraint(
            model_name='product',
            constraint=models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='product_price_positive'
            ),
        ),
        
        # 5. Run custom SQL
        migrations.RunSQL(
            sql="CREATE INDEX CONCURRENTLY product_name_search ON myapp_product USING gin(to_tsvector('english', name));",
            reverse_sql="DROP INDEX IF EXISTS product_name_search;",
        ),
        
        # 6. Populate initial data
        migrations.RunPython(
            code=populate_initial_data,
            reverse_code=remove_initial_data,
        ),
        
        # 7. Alter model options
        migrations.AlterModelOptions(
            name='product',
            options={
                'ordering': ['category__name', 'name'],
                'permissions': [
                    ('can_view_analytics', 'Can view product analytics'),
                ],
            },
        ),
    ]
'''
    
    print(migration_example)


def show_best_practices():
    """
    Shows migration best practices
    """
    print("\n" + "="*60)
    print("MIGRATION BEST PRACTICES")
    print("="*60)
    
    practices = """
1. OPERATION ORDERING:
   - Create models before adding relationships
   - Add fields before creating indexes on them
   - Remove constraints before removing fields

2. REVERSIBILITY:
   - Always provide reverse_code for RunPython
   - Use preserve_default=False for temporary defaults
   - Consider data loss in RemoveField operations

3. PERFORMANCE:
   - Use CONCURRENTLY for index creation in PostgreSQL
   - Add nullable fields first, then make them required
   - Batch data operations in RunPython

4. DATA SAFETY:
   - Test migrations on copy of production data
   - Use atomic=False for long-running operations
   - Backup database before complex migrations

5. CUSTOM OPERATIONS:
   - Extend Operation base class for reusable logic
   - Implement state_forwards() and database_forwards()
   - Use proper migration_name_fragment

6. DEPENDENCY MANAGEMENT:
   - Specify correct dependencies
   - Handle circular dependencies carefully
   - Use squash migrations for cleanup

7. SQL OPERATIONS:
   - Use schema_editor.execute() for database operations
   - Handle different database backends
   - Escape SQL parameters properly

8. PYTHON OPERATIONS:
   - Use apps.get_model() for historical models
   - Handle database routing with db_alias
   - Don't import models directly in migration code
"""
    
    print(practices)


def check_current_migrations():
    """
    Check current migration status
    """
    print("\n" + "="*60)
    print("CURRENT MIGRATION STATUS")
    print("="*60)
    
    from django.db.migrations.executor import MigrationExecutor
    from django.db import connection
    
    try:
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print("Pending migrations:")
            for migration, backwards in plan:
                direction = "BACKWARDS" if backwards else "FORWARDS"
                print(f"  {migration.app_label}.{migration.name} ({direction})")
        else:
            print("All migrations are up to date!")
            
        # Show applied migrations for current app
        from django.db.migrations.recorder import MigrationRecorder
        recorder = MigrationRecorder(connection)
        applied = recorder.applied_migrations()
        
        app_migrations = [m for m in applied if m[0] == 'model_class_practice']
        if app_migrations:
            print(f"\nApplied migrations for model_class_practice:")
            for app, name in sorted(app_migrations):
                print(f"  {app}.{name}")
                
    except Exception as e:
        print(f"Error checking migration status: {e}")


if __name__ == "__main__":
    demonstrate_migration_operations()
    show_migration_file_example()
    show_best_practices()
    check_current_migrations()
