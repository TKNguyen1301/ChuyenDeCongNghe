#!/usr/bin/env python3
"""
Django Migration Operations - Hands-on Practice Script
=====================================================

This script demonstrates step-by-step migration operations practice.
Run: python migration_operations_demo.py
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import migrations, models
import django.db.models.deletion


def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modelspractice.settings')
    django.setup()


def create_custom_migration_operations():
    """
    Demonstrates how to create custom migration files with specific operations
    """
    print("=" * 60)
    print("CREATING CUSTOM MIGRATION OPERATIONS")
    print("=" * 60)
    
    # Custom migration content for different operation types
    migration_templates = {
        'schema_operations': '''
# Generated migration for schema operations practice
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    
    dependencies = [
        ('model_class_practice', '0001_initial'),
    ]
    
    operations = [
        # 1. Create a new model
        migrations.CreateModel(
            name='MigrationTestModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Migration Test Model',
                'ordering': ['-created_at'],
            },
        ),
        
        # 2. Add a field
        migrations.AddField(
            model_name='migrationtestmodel',
            name='description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        
        # 3. Alter a field
        migrations.AlterField(
            model_name='migrationtestmodel',
            name='title',
            field=models.CharField(max_length=300, help_text='Title of the item'),
        ),
        
        # 4. Add an index
        migrations.AddIndex(
            model_name='migrationtestmodel',
            index=models.Index(fields=['title', 'created_at'], name='test_title_created_idx'),
        ),
        
        # 5. Add a constraint
        migrations.AddConstraint(
            model_name='migrationtestmodel',
            constraint=models.CheckConstraint(
                check=models.Q(title__isnull=False),
                name='test_title_not_null'
            ),
        ),
    ]
''',
        
        'data_operations': '''
# Generated migration for data operations practice
from django.db import migrations


def create_sample_data(apps, schema_editor):
    """Create some sample data"""
    MigrationTestModel = apps.get_model('model_class_practice', 'MigrationTestModel')
    db_alias = schema_editor.connection.alias
    
    # Create sample records
    MigrationTestModel.objects.using(db_alias).bulk_create([
        MigrationTestModel(title='Sample Item 1', description='First test item'),
        MigrationTestModel(title='Sample Item 2', description='Second test item'),
        MigrationTestModel(title='Sample Item 3', description='Third test item'),
    ])


def remove_sample_data(apps, schema_editor):
    """Remove the sample data"""
    MigrationTestModel = apps.get_model('model_class_practice', 'MigrationTestModel')
    db_alias = schema_editor.connection.alias
    
    # Remove sample records
    MigrationTestModel.objects.using(db_alias).filter(
        title__startswith='Sample Item'
    ).delete()


def update_existing_data(apps, schema_editor):
    """Update existing data"""
    MigrationTestModel = apps.get_model('model_class_practice', 'MigrationTestModel')
    db_alias = schema_editor.connection.alias
    
    # Update records
    MigrationTestModel.objects.using(db_alias).filter(
        description=''
    ).update(description='Updated description')


class Migration(migrations.Migration):
    
    dependencies = [
        ('model_class_practice', '0002_schema_operations'),
    ]
    
    operations = [
        # 1. Populate initial data
        migrations.RunPython(
            code=create_sample_data,
            reverse_code=remove_sample_data,
        ),
        
        # 2. Update existing data
        migrations.RunPython(
            code=update_existing_data,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
''',
        
        'sql_operations': '''
# Generated migration for SQL operations practice
from django.db import migrations


class Migration(migrations.Migration):
    
    dependencies = [
        ('model_class_practice', '0003_data_operations'),
    ]
    
    operations = [
        # 1. Create custom index with SQL
        migrations.RunSQL(
            sql="CREATE INDEX CONCURRENTLY IF NOT EXISTS test_title_gin ON model_class_practice_migrationtestmodel USING gin(to_tsvector('english', title));",
            reverse_sql="DROP INDEX IF EXISTS test_title_gin;",
        ),
        
        # 2. Create a custom function
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION update_test_model_timestamp()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.created_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS update_test_model_timestamp();",
        ),
        
        # 3. Add custom table comment
        migrations.RunSQL(
            sql="COMMENT ON TABLE model_class_practice_migrationtestmodel IS 'Test table for migration operations';",
            reverse_sql="COMMENT ON TABLE model_class_practice_migrationtestmodel IS NULL;",
        ),
    ]
''',
        
        'cleanup_operations': '''
# Generated migration for cleanup operations
from django.db import migrations


class Migration(migrations.Migration):
    
    dependencies = [
        ('model_class_practice', '0004_sql_operations'),
    ]
    
    operations = [
        # 1. Remove constraint
        migrations.RemoveConstraint(
            model_name='migrationtestmodel',
            name='test_title_not_null',
        ),
        
        # 2. Remove index
        migrations.RemoveIndex(
            model_name='migrationtestmodel',
            name='test_title_created_idx',
        ),
        
        # 3. Remove field
        migrations.RemoveField(
            model_name='migrationtestmodel',
            name='description',
        ),
        
        # 4. Rename model
        migrations.RenameModel(
            old_name='MigrationTestModel',
            new_name='ArchivedTestModel',
        ),
        
        # 5. Finally delete the model
        migrations.DeleteModel(
            name='ArchivedTestModel',
        ),
    ]
'''
    }
    
    return migration_templates


def demonstrate_migration_commands():
    """
    Demonstrates various Django migration management commands
    """
    print("\\n" + "=" * 60)
    print("DJANGO MIGRATION COMMANDS REFERENCE")
    print("=" * 60)
    
    commands = {
        "Basic Commands": [
            ("python manage.py makemigrations", "Create new migrations based on model changes"),
            ("python manage.py migrate", "Apply pending migrations"),
            ("python manage.py showmigrations", "Show migration status"),
            ("python manage.py sqlmigrate app_name 0001", "Show SQL for a specific migration"),
        ],
        
        "Advanced Commands": [
            ("python manage.py makemigrations --empty app_name", "Create empty migration file"),
            ("python manage.py makemigrations --dry-run", "Show what migrations would be created"),
            ("python manage.py migrate --fake", "Mark migrations as applied without running"),
            ("python manage.py migrate app_name 0001", "Migrate to specific migration"),
            ("python manage.py migrate app_name zero", "Undo all migrations for app"),
        ],
        
        "Debugging Commands": [
            ("python manage.py check", "Check for issues without making migrations"),
            ("python manage.py migrate --plan", "Show migration plan"),
            ("python manage.py showmigrations --plan", "Show detailed migration plan"),
            ("python manage.py squashmigrations app_name 0001 0005", "Squash multiple migrations"),
        ]
    }
    
    for category, cmd_list in commands.items():
        print(f"\\n{category}:")
        print("-" * len(category))
        for cmd, desc in cmd_list:
            print(f"  {cmd}")
            print(f"    → {desc}")


def show_migration_troubleshooting():
    """
    Common migration issues and solutions
    """
    print("\\n" + "=" * 60)
    print("MIGRATION TROUBLESHOOTING GUIDE")
    print("=" * 60)
    
    issues = {
        "Dependency Issues": {
            "Problem": "Migrations with circular dependencies",
            "Solutions": [
                "Use --merge flag: python manage.py makemigrations --merge",
                "Manually edit migration dependencies",
                "Split complex migrations into smaller ones"
            ]
        },
        
        "Fake Migration Issues": {
            "Problem": "Database state doesn't match migration state", 
            "Solutions": [
                "Use --fake-initial for initial migrations",
                "Reset migrations: delete migration files and migrate --fake",
                "Use migrate --fake to mark specific migrations as applied"
            ]
        },
        
        "Schema Conflicts": {
            "Problem": "Database schema conflicts with model definitions",
            "Solutions": [
                "Use django-extensions: python manage.py reset_db",
                "Manual database cleanup",
                "Use --run-syncdb for fresh databases"
            ]
        },
        
        "Performance Issues": {
            "Problem": "Long-running migrations in production",
            "Solutions": [
                "Use database-specific optimizations (CONCURRENTLY in PostgreSQL)",
                "Split large data migrations into smaller batches", 
                "Use atomic=False for non-transactional operations",
                "Run migrations during maintenance windows"
            ]
        }
    }
    
    for issue, details in issues.items():
        print(f"\\n{issue}:")
        print(f"Problem: {details['Problem']}")
        print("Solutions:")
        for solution in details['Solutions']:
            print(f"  • {solution}")


def create_practice_workflow():
    """
    Creates a step-by-step practice workflow
    """
    print("\\n" + "=" * 60)
    print("MIGRATION OPERATIONS PRACTICE WORKFLOW")
    print("=" * 60)
    
    workflow = """
STEP 1: Setup and Initial State
-------------------------------
1. Check current migration status:
   python manage.py showmigrations model_class_practice

2. Create a backup of current database:
   python manage.py dumpdata > backup.json

STEP 2: Schema Operations Practice
----------------------------------
1. Create empty migration:
   python manage.py makemigrations model_class_practice --empty --name schema_operations

2. Edit the migration file to add schema operations:
   - CreateModel
   - AddField, RemoveField, AlterField
   - AddIndex, RemoveIndex  
   - AddConstraint, RemoveConstraint

3. Apply migration:
   python manage.py migrate

4. Check SQL output:
   python manage.py sqlmigrate model_class_practice 0002

STEP 3: Data Operations Practice
--------------------------------
1. Create data migration:
   python manage.py makemigrations model_class_practice --empty --name data_operations

2. Add RunPython operations:
   - Create sample data
   - Update existing data
   - Data transformations

3. Test forward and reverse:
   python manage.py migrate
   python manage.py migrate model_class_practice 0002  # reverse
   python manage.py migrate  # forward again

STEP 4: SQL Operations Practice
-------------------------------
1. Create SQL migration:
   python manage.py makemigrations model_class_practice --empty --name sql_operations

2. Add RunSQL operations:
   - Custom indexes
   - Database functions
   - Views and triggers

3. Test on different databases if available

STEP 5: Cleanup and Rollback
-----------------------------
1. Create cleanup migration:
   python manage.py makemigrations model_class_practice --empty --name cleanup

2. Practice removing operations:
   - Remove constraints and indexes
   - Remove fields
   - Rename/delete models

3. Test full rollback:
   python manage.py migrate model_class_practice zero
   python manage.py migrate  # reapply all

STEP 6: Advanced Scenarios
---------------------------
1. Practice squashing migrations:
   python manage.py squashmigrations model_class_practice 0002 0005

2. Practice merge conflicts:
   - Create conflicting migrations in different branches
   - Use --merge flag

3. Practice production scenarios:
   - Large data migrations
   - Zero-downtime deployments
   - Rolling back problematic migrations
"""
    
    print(workflow)


def main():
    """Main execution function"""
    print("Django Migration Operations - Complete Practice Guide")
    print("=" * 60)
    
    try:
        setup_django()
        
        # Run demonstrations
        templates = create_custom_migration_operations()
        
        print("Migration templates created for:")
        for name in templates.keys():
            print(f"  • {name}")
        
        demonstrate_migration_commands()
        show_migration_troubleshooting()
        create_practice_workflow()
        
        print("\\n" + "=" * 60)
        print("NEXT STEPS:")
        print("1. Run: python manage.py shell < migration_operations_practice.py")
        print("2. Practice creating actual migrations with the workflow above")
        print("3. Experiment with different operation combinations")
        print("4. Test rollback scenarios")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you're in the correct Django project directory")


if __name__ == "__main__":
    main()
