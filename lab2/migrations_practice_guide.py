#!/usr/bin/env python
"""
Django Migrations Interactive Practice Guide
Following https://docs.djangoproject.com/en/5.2/topics/migrations/

Comprehensive hands-on practice with Django migrations including:
- Basic migration commands
- Schema migrations
- Data migrations
- Migration dependencies
- Squashing migrations
- Best practices and troubleshooting
"""

import os
import sys
import django

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modelspractice.settings')
    django.setup()

from django.db import models, migrations
from django.core.management import call_command
from django.apps import apps
from datetime import datetime, timedelta
import subprocess
import json


class MigrationsPracticeGuide:
    """Interactive guide for Django Migrations practice."""
    
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
    
    def run_command(self, command, description=""):
        """Run a Django management command."""
        if description:
            print(f"\n🔧 {description}")
        try:
            print(f"Running: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd="/Users/nguyen/Downloads/ChuyenDeCongNghe/lab2")
            if result.stdout:
                print(f"Output:\n{result.stdout}")
            if result.stderr:
                print(f"Error:\n{result.stderr}")
            return result.returncode == 0
        except Exception as e:
            print(f"Command failed: {e}")
            return False


def section_1_migration_commands(guide):
    """Section 1: Master Migration Commands"""
    guide.print_header("Master Migration Commands")
    
    print("""
📚 THEORY: Django provides several commands for migration management:
• makemigrations: Creates new migrations based on model changes
• migrate: Applies and unapplies migrations
• sqlmigrate: Shows SQL for a migration
• showmigrations: Lists migrations and their status

MIGRATION WORKFLOW:
1. Modify models.py
2. Run makemigrations to create migration files
3. Review the generated migration
4. Run migrate to apply to database
5. Commit migration files to version control
""")
    
    guide.print_header("Check Current Migration Status", 2)
    guide.print_task("Use showmigrations to see current state of all migrations")
    guide.print_hint("The showmigrations command shows [X] for applied, [ ] for unapplied")
    guide.wait_for_user()
    
    guide.print_solution([
        "python manage.py showmigrations",
        "",
        "# Show specific app:",
        "python manage.py showmigrations blog",
        "",
        "# Show in list format:",
        "python manage.py showmigrations --list"
    ], "showmigrations helps you understand the current state of your database")
    
    success = guide.run_command("python manage.py showmigrations", "Checking migration status")
    
    guide.print_header("View SQL for Migration", 2)
    guide.print_task("Use sqlmigrate to see the actual SQL that will be executed")
    guide.print_hint("This helps understand what Django will do to your database")
    guide.wait_for_user()
    
    guide.print_solution([
        "python manage.py sqlmigrate blog 0001",
        "",
        "# Format: app_label migration_number",
        "# Example: python manage.py sqlmigrate query_practice 0001_initial"
    ], "sqlmigrate shows the SQL without executing it - great for reviewing changes")
    
    # Try to show SQL for an existing migration
    success = guide.run_command("python manage.py sqlmigrate blog 0001", "Viewing SQL for blog migration")
    
    guide.print_header("Dry Run Migrations", 2)
    guide.print_task("Use --dry-run flag to see what migrations would be created")
    guide.print_hint("Always check what Django plans to do before creating migrations")
    guide.wait_for_user()
    
    guide.print_solution([
        "python manage.py makemigrations --dry-run",
        "",
        "# For specific app:",
        "python manage.py makemigrations --dry-run blog",
        "",
        "# With verbosity for more details:",
        "python manage.py makemigrations --dry-run --verbosity=2"
    ], "Dry run prevents accidental migration creation and shows what would happen")
    
    success = guide.run_command("python manage.py makemigrations --dry-run", "Dry run check")


def section_2_schema_migrations(guide):
    """Section 2: Schema Migrations"""
    guide.print_header("Schema Migrations")
    
    print("""
🔧 THEORY: Schema migrations handle database structure changes:
• Adding/removing fields
• Creating/deleting models
• Changing field types
• Adding/removing indexes
• Modifying constraints

AUTODETECTION: Django compares current models with migration history
to detect changes automatically.
""")
    
    guide.print_header("Create Practice Model Changes", 2)
    guide.print_task("Let's create a new model to practice with")
    guide.print_hint("We'll add a new model to one of our existing apps")
    guide.wait_for_user()
    
    # Create a temporary model file for practice
    practice_model = '''
from django.db import models

class MigrationPractice(models.Model):
    """Model for practicing migrations"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'migration_practice'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
'''
    
    guide.print_solution([
        "# Add to blog/models.py:",
        "class MigrationPractice(models.Model):",
        "    title = models.CharField(max_length=200)",
        "    description = models.TextField()",
        "    created_at = models.DateTimeField(auto_now_add=True)",
        "    is_active = models.BooleanField(default=True)",
        "    ",
        "    class Meta:",
        "        db_table = 'migration_practice'",
        "        ordering = ['-created_at']"
    ], "New models trigger CREATE TABLE migrations")
    
    # Add the model to blog app
    try:
        with open('/Users/nguyen/Downloads/ChuyenDeCongNghe/lab2/blog/models.py', 'a') as f:
            f.write(f"\n\n{practice_model}")
        print("✅ Added MigrationPractice model to blog/models.py")
    except Exception as e:
        print(f"❌ Could not add model: {e}")
    
    guide.print_header("Create Migration for New Model", 2)
    guide.print_task("Generate migration for the new model")
    guide.print_hint("Use makemigrations with app name for targeted migration")
    guide.wait_for_user()
    
    guide.print_solution([
        "python manage.py makemigrations blog",
        "",
        "# With custom name:",
        "python manage.py makemigrations blog --name add_migration_practice",
        "",
        "# With description:",
        "python manage.py makemigrations blog --name add_practice_model"
    ], "Always review generated migrations before applying them")
    
    success = guide.run_command("python manage.py makemigrations blog --name add_practice_model", 
                               "Creating migration for new model")
    
    guide.print_header("Apply the Migration", 2)
    guide.print_task("Apply the new migration to the database")
    guide.print_hint("Use migrate command to execute the migration")
    guide.wait_for_user()
    
    guide.print_solution([
        "python manage.py migrate blog",
        "",
        "# Or migrate all apps:",
        "python manage.py migrate",
        "",
        "# With verbosity for details:",
        "python manage.py migrate --verbosity=2"
    ], "migrate command executes the SQL to update database schema")
    
    success = guide.run_command("python manage.py migrate blog", "Applying migration")
    
    guide.print_header("Add Field Migration", 2)
    guide.print_task("Add a new field to existing model and create migration")
    guide.print_hint("Modify the MigrationPractice model to add a field")
    guide.wait_for_user()
    
    # Add a field to the practice model
    additional_field = '''
    # Add this field to MigrationPractice model:
    priority = models.IntegerField(default=1, choices=[
        (1, 'Low'),
        (2, 'Medium'), 
        (3, 'High'),
    ])
'''
    
    guide.print_solution([
        "# Add to MigrationPractice model:",
        "priority = models.IntegerField(default=1, choices=[",
        "    (1, 'Low'),",
        "    (2, 'Medium'),",
        "    (3, 'High'),",
        "])",
        "",
        "# Then run:",
        "python manage.py makemigrations blog",
        "python manage.py migrate blog"
    ], "Adding fields with defaults is safe - no data loss")
    
    print(f"\n{additional_field}")


def section_3_data_migrations(guide):
    """Section 3: Data Migrations"""
    guide.print_header("Data Migrations")
    
    print("""
💾 THEORY: Data migrations modify database content, not structure:
• Populate new fields with calculated values
• Transform existing data
• Clean up data inconsistencies
• Seed initial data

KEY CONCEPTS:
• Use RunPython operation for data changes
• Access historical models via apps.get_model()
• Write reversible operations when possible
• Separate data migrations from schema migrations
""")
    
    guide.print_header("Create Empty Data Migration", 2)
    guide.print_task("Create an empty migration file for data operations")
    guide.print_hint("Use --empty flag to create migration template")
    guide.wait_for_user()
    
    guide.print_solution([
        "python manage.py makemigrations --empty blog",
        "",
        "# With descriptive name:",
        "python manage.py makemigrations --empty blog --name populate_initial_data"
    ], "Empty migrations provide template for custom operations")
    
    success = guide.run_command("python manage.py makemigrations --empty blog --name populate_initial_data",
                               "Creating empty migration")
    
    guide.print_header("Write Data Migration Function", 2)
    guide.print_task("Create a function to populate initial data")
    guide.print_hint("Use RunPython with forward and reverse functions")
    guide.wait_for_user()
    
    data_migration_example = '''
from django.db import migrations

def populate_practice_data(apps, schema_editor):
    """Forward data migration - populate initial data"""
    MigrationPractice = apps.get_model('blog', 'MigrationPractice')
    
    # Create sample data
    sample_data = [
        {
            'title': 'Migration Best Practices',
            'description': 'Learn how to write effective Django migrations',
            'is_active': True,
            'priority': 3
        },
        {
            'title': 'Database Optimization',
            'description': 'Techniques for optimizing database performance',
            'is_active': True,
            'priority': 2
        },
        {
            'title': 'Legacy Code Cleanup',
            'description': 'Strategies for cleaning up old code',
            'is_active': False,
            'priority': 1
        }
    ]
    
    for data in sample_data:
        MigrationPractice.objects.create(**data)

def reverse_populate_data(apps, schema_editor):
    """Reverse data migration - clean up data"""
    MigrationPractice = apps.get_model('blog', 'MigrationPractice')
    MigrationPractice.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0002_add_practice_model'),  # Depends on previous migration
    ]

    operations = [
        migrations.RunPython(
            populate_practice_data,
            reverse_populate_data
        ),
    ]
'''
    
    guide.print_solution([
        "# Create functions for forward and reverse operations:",
        "def populate_practice_data(apps, schema_editor):",
        "    MigrationPractice = apps.get_model('blog', 'MigrationPractice')",
        "    # Use historical model, not direct import",
        "    ",
        "    sample_data = [...]",
        "    for data in sample_data:",
        "        MigrationPractice.objects.create(**data)",
        "",
        "def reverse_populate_data(apps, schema_editor):",
        "    MigrationPractice = apps.get_model('blog', 'MigrationPractice')",
        "    MigrationPractice.objects.all().delete()",
        "",
        "# Add to migration operations:",
        "migrations.RunPython(populate_practice_data, reverse_populate_data)"
    ], "Always use historical models (apps.get_model) in data migrations")
    
    print(f"\n📋 COMPLETE EXAMPLE:\n{data_migration_example}")
    
    guide.print_header("Advanced Data Transformation", 2)
    guide.print_task("Write a migration that transforms existing data")
    guide.print_hint("Example: combining first_name + last_name into full_name field")
    guide.wait_for_user()
    
    transformation_example = '''
def combine_names(apps, schema_editor):
    """Combine first and last names into full name"""
    Person = apps.get_model('yourapp', 'Person')
    
    for person in Person.objects.all():
        if person.first_name and person.last_name:
            person.full_name = f"{person.first_name} {person.last_name}"
        elif person.first_name:
            person.full_name = person.first_name
        elif person.last_name:
            person.full_name = person.last_name
        else:
            person.full_name = "Unknown"
        person.save()

def split_names(apps, schema_editor):
    """Reverse operation - split full name back"""
    Person = apps.get_model('yourapp', 'Person')
    
    for person in Person.objects.all():
        if person.full_name:
            parts = person.full_name.split(' ', 1)
            person.first_name = parts[0]
            person.last_name = parts[1] if len(parts) > 1 else ''
            person.save()
'''
    
    guide.print_solution([
        "# Data transformation pattern:",
        "def transform_data(apps, schema_editor):",
        "    Model = apps.get_model('app', 'Model')",
        "    ",
        "    for obj in Model.objects.all():",
        "        # Transform the data",
        "        obj.new_field = calculate_value(obj.old_field)",
        "        obj.save()",
        "",
        "# Always provide reverse operation:",
        "def reverse_transform(apps, schema_editor):",
        "    # Undo the transformation",
        "    pass"
    ], "Data transformations should be reversible when possible")
    
    print(f"\n📋 TRANSFORMATION EXAMPLE:\n{transformation_example}")


def section_4_migration_dependencies(guide):
    """Section 4: Migration Dependencies and Conflicts"""
    guide.print_header("Migration Dependencies and Conflicts")
    
    print("""
🔗 THEORY: Migrations form a directed graph based on dependencies:
• Each migration specifies which migrations it depends on
• Django resolves the correct order automatically
• Conflicts arise when parallel development creates branching
• Manual resolution required for complex dependency issues

DEPENDENCY TYPES:
• Same app dependencies: Sequential migrations in one app
• Cross-app dependencies: ForeignKey relationships between apps
• Swappable dependencies: Custom user models, etc.
""")
    
    guide.print_header("Understanding Dependencies", 2)
    guide.print_task("Examine migration dependencies in existing files")
    guide.print_hint("Look at the dependencies list in migration files")
    guide.wait_for_user()
    
    guide.print_solution([
        "# Check migration file structure:",
        "cat blog/migrations/0001_initial.py",
        "",
        "# Look for dependencies list:",
        "dependencies = [",
        "    ('auth', '0012_alter_user_first_name_max_length'),",
        "]",
        "",
        "# Check migration graph:",
        "python manage.py showmigrations --plan"
    ], "Dependencies ensure migrations run in correct order")
    
    # Show migration dependencies
    success = guide.run_command("python manage.py showmigrations --plan", "Showing migration plan")
    
    guide.print_header("Simulate Migration Conflict", 2)
    guide.print_task("Understand how migration conflicts arise and resolve them")
    guide.print_hint("Conflicts happen when two developers create migrations with same number")
    guide.wait_for_user()
    
    conflict_example = '''
# Developer A creates:
blog/migrations/0003_add_author_field.py

# Developer B creates (at same time):
blog/migrations/0003_add_category_field.py

# Git merge creates conflict - two migrations with same number!

# Django detects this and offers to fix:
$ python manage.py makemigrations
You have migrations that run after each other. This is indicative of a
branching in your migration graph. Please fix this with:
    python manage.py makemigrations --merge
'''
    
    guide.print_solution([
        "# When conflict detected:",
        "python manage.py makemigrations --merge",
        "",
        "# Django creates merge migration automatically:",
        "dependencies = [",
        "    ('blog', '0003_add_author_field'),",
        "    ('blog', '0003_add_category_field'),",
        "]",
        "",
        "# Manual resolution for complex conflicts:",
        "# Edit migration files to fix dependency order"
    ], "Use --merge flag for automatic conflict resolution")
    
    print(f"\n📋 CONFLICT EXAMPLE:\n{conflict_example}")
    
    guide.print_header("Cross-App Dependencies", 2)
    guide.print_task("Create migration with dependencies on other apps")
    guide.print_hint("ForeignKey fields create automatic dependencies")
    guide.wait_for_user()
    
    cross_app_example = '''
# When adding ForeignKey to User model:
class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
# Django automatically adds dependency:
dependencies = [
    ('blog', '0002_previous_migration'),
    ('auth', '0012_alter_user_first_name_max_length'),
]

# For custom dependencies:
dependencies = [
    ('blog', '0002_previous'),
    ('auth', '__latest__'),  # Latest auth migration
]
'''
    
    guide.print_solution([
        "# Automatic dependencies for ForeignKey:",
        "class Post(models.Model):",
        "    author = models.ForeignKey(User, on_delete=models.CASCADE)",
        "",
        "# Manual dependencies:",
        "dependencies = [",
        "    ('myapp', '0001_initial'),",
        "    ('auth', '__latest__'),",
        "]",
        "",
        "# Swappable dependencies:",
        "dependencies = [",
        "    migrations.swappable_dependency(settings.AUTH_USER_MODEL),",
        "]"
    ], "Cross-app dependencies ensure referential integrity")
    
    print(f"\n📋 CROSS-APP EXAMPLE:\n{cross_app_example}")


def section_5_advanced_operations(guide):
    """Section 5: Advanced Migration Operations"""
    guide.print_header("Advanced Migration Operations")
    
    print("""
⚙️ THEORY: Beyond basic model operations, Django supports:
• Custom SQL execution with RunSQL
• Python code execution with RunPython
• Database schema manipulation
• Non-atomic operations
• Custom migration operations

WHEN TO USE:
• Database-specific features (triggers, functions)
• Complex data transformations
• Performance-critical operations
• Integration with external systems
""")
    
    guide.print_header("Custom SQL Operations", 2)
    guide.print_task("Execute custom SQL in migrations")
    guide.print_hint("Use RunSQL for database-specific features")
    guide.wait_for_user()
    
    sql_example = '''
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0003_previous'),
    ]

    operations = [
        # Create database index
        migrations.RunSQL(
            sql="CREATE INDEX idx_blog_title_gin ON blog_post USING GIN(to_tsvector('english', title));",
            reverse_sql="DROP INDEX idx_blog_title_gin;"
        ),
        
        # Create database function
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION update_modified_time()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.modified_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            """,
            reverse_sql="DROP FUNCTION update_modified_time();"
        ),
        
        # Create trigger
        migrations.RunSQL(
            sql="""
            CREATE TRIGGER update_blog_modified_time
                BEFORE UPDATE ON blog_post
                FOR EACH ROW
                EXECUTE FUNCTION update_modified_time();
            """,
            reverse_sql="DROP TRIGGER update_blog_modified_time ON blog_post;"
        ),
    ]
'''
    
    guide.print_solution([
        "# Basic SQL execution:",
        "migrations.RunSQL(",
        "    sql='CREATE INDEX idx_title ON app_model(title);',",
        "    reverse_sql='DROP INDEX idx_title;'",
        ")",
        "",
        "# Database function creation:",
        "migrations.RunSQL(",
        "    sql='CREATE FUNCTION ...;',",
        "    reverse_sql='DROP FUNCTION ...;'",
        ")",
        "",
        "# State operations (no SQL):",
        "migrations.RunSQL(",
        "    sql=migrations.RunSQL.noop,",
        "    reverse_sql=migrations.RunSQL.noop,",
        "    state_operations=[migrations.AddField(...)]",
        ")"
    ], "RunSQL allows database-specific optimizations and features")
    
    print(f"\n📋 SQL EXAMPLE:\n{sql_example}")
    
    guide.print_header("Non-Atomic Operations", 2)
    guide.print_task("Create migration that doesn't run in transaction")
    guide.print_hint("Use atomic=False for operations that can't be rolled back")
    guide.wait_for_user()
    
    non_atomic_example = '''
from django.db import migrations

class Migration(migrations.Migration):
    atomic = False  # Disable transaction wrapping
    
    dependencies = [
        ('blog', '0004_previous'),
    ]

    operations = [
        # Large data migration that might take long time
        migrations.RunPython(
            code=migrate_large_dataset,
            reverse_code=migrations.RunPython.noop,
            atomic=True  # This operation can still be atomic
        ),
        
        # Operation that must run outside transaction
        migrations.RunSQL(
            sql="CREATE INDEX CONCURRENTLY idx_concurrent ON large_table(column);",
            reverse_sql="DROP INDEX idx_concurrent;",
            atomic=False
        ),
    ]
'''
    
    guide.print_solution([
        "# Disable transaction for entire migration:",
        "class Migration(migrations.Migration):",
        "    atomic = False",
        "",
        "# Disable transaction for specific operation:",
        "migrations.RunPython(",
        "    code=my_function,",
        "    atomic=False",
        ")",
        "",
        "# Use when:",
        "# - Creating indexes concurrently",
        "# - Large data migrations",
        "# - Operations that can't be rolled back"
    ], "Non-atomic operations trade safety for performance/compatibility")
    
    print(f"\n📋 NON-ATOMIC EXAMPLE:\n{non_atomic_example}")
    
    guide.print_header("Custom Migration Operations", 2)
    guide.print_task("Create a custom migration operation class")
    guide.print_hint("Inherit from Operation class for reusable migration logic")
    guide.wait_for_user()
    
    custom_operation_example = '''
from django.db import migrations
from django.db.migrations.operations.base import Operation

class CreateExtension(Operation):
    """Custom operation to create PostgreSQL extensions"""
    
    reversible = True
    
    def __init__(self, name):
        self.name = name
    
    def state_forwards(self, app_label, state):
        # This operation doesn't change model state
        pass
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(f"CREATE EXTENSION IF NOT EXISTS {self.name};")
    
    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(f"DROP EXTENSION {self.name};")
    
    def describe(self):
        return f"Create extension {self.name}"

# Usage in migration:
class Migration(migrations.Migration):
    operations = [
        CreateExtension('pg_trgm'),
        CreateExtension('unaccent'),
    ]
'''
    
    guide.print_solution([
        "# Custom operation structure:",
        "class CustomOperation(Operation):",
        "    reversible = True",
        "    ",
        "    def state_forwards(self, app_label, state):",
        "        # Update Django's model state",
        "        pass",
        "    ",
        "    def database_forwards(self, app_label, schema_editor, ...):",
        "        # Execute forward database changes",
        "        schema_editor.execute('SQL...')",
        "    ",
        "    def database_backwards(self, app_label, schema_editor, ...):",
        "        # Execute reverse database changes",
        "        schema_editor.execute('REVERSE SQL...')"
    ], "Custom operations encapsulate reusable migration logic")
    
    print(f"\n📋 CUSTOM OPERATION EXAMPLE:\n{custom_operation_example}")


def section_6_migration_best_practices(guide):
    """Section 6: Migration Best Practices and Troubleshooting"""
    guide.print_header("Migration Best Practices and Troubleshooting")
    
    print("""
🎯 THEORY: Professional migration management requires:
• Proper testing procedures
• Performance considerations
• Rollback strategies
• Team collaboration workflows
• Production deployment best practices

GOLDEN RULES:
1. Always review generated migrations
2. Test migrations on production-like data
3. Consider performance impact
4. Plan rollback procedures
5. Coordinate with team members
""")
    
    guide.print_header("Migration Testing Strategy", 2)
    guide.print_task("Develop comprehensive testing approach for migrations")
    guide.print_hint("Test on copy of production data, measure performance")
    guide.wait_for_user()
    
    testing_strategy = '''
# 1. Test migration generation
python manage.py makemigrations --dry-run --verbosity=2

# 2. Review generated SQL
python manage.py sqlmigrate app_name migration_number

# 3. Test on development data
python manage.py migrate

# 4. Test rollback capability
python manage.py migrate app_name previous_migration

# 5. Performance testing with production-like data
python manage.py migrate --verbosity=2

# 6. Test in staging environment
# Copy production database to staging
# Run migrations and verify results

# 7. Plan rollback strategy
# Document rollback procedures
# Test rollback with sample data
'''
    
    guide.print_solution([
        "# Complete testing workflow:",
        "1. python manage.py makemigrations --dry-run",
        "2. python manage.py sqlmigrate app migration",
        "3. Test on development copy",
        "4. Test rollback: migrate app previous_migration",
        "5. Performance test with large dataset",
        "6. Deploy to staging first",
        "7. Document rollback procedures",
        "",
        "# Performance testing:",
        "time python manage.py migrate --verbosity=2"
    ], "Comprehensive testing prevents production issues")
    
    print(f"\n📋 TESTING STRATEGY:\n{testing_strategy}")
    
    guide.print_header("Performance Considerations", 2)
    guide.print_task("Optimize migrations for large datasets")
    guide.print_hint("Consider locking, indexing, and batch processing")
    guide.wait_for_user()
    
    performance_tips = '''
# 1. Add indexes before adding constraints
class Migration(migrations.Migration):
    operations = [
        # Add index first
        migrations.RunSQL("CREATE INDEX idx_temp ON table(column);"),
        # Then add foreign key
        migrations.AddField('Model', 'field', models.ForeignKey(...)),
        # Remove temporary index if needed
        migrations.RunSQL("DROP INDEX idx_temp;"),
    ]

# 2. Use batch processing for large data migrations
def migrate_data_in_batches(apps, schema_editor):
    Model = apps.get_model('app', 'Model')
    batch_size = 1000
    
    for start in range(0, Model.objects.count(), batch_size):
        batch = Model.objects.all()[start:start + batch_size]
        for obj in batch:
            # Process object
            obj.new_field = calculate_value(obj)
        Model.objects.bulk_update(batch, ['new_field'])

# 3. Consider table locks and downtime
# For very large tables, plan maintenance window
# Use atomic=False for long-running operations
# Consider online schema change tools for critical systems
'''
    
    guide.print_solution([
        "# Performance optimization strategies:",
        "1. Add indexes before constraints",
        "2. Use bulk operations for data changes",
        "3. Process data in batches",
        "4. Consider atomic=False for long operations",
        "5. Plan maintenance windows for large changes",
        "",
        "# Example batch processing:",
        "def migrate_in_batches(apps, schema_editor):",
        "    Model = apps.get_model('app', 'Model')",
        "    batch_size = 1000",
        "    # Process in chunks to avoid memory issues"
    ], "Performance planning prevents production downtime")
    
    print(f"\n📋 PERFORMANCE TIPS:\n{performance_tips}")
    
    guide.print_header("Troubleshooting Common Issues", 2)
    guide.print_task("Learn to diagnose and fix migration problems")
    guide.print_hint("Common issues: fake migrations, state inconsistencies, dependency loops")
    guide.wait_for_user()
    
    troubleshooting_guide = '''
# 1. Inconsistent migration state
# Problem: Migration shows as applied but table doesn't exist
python manage.py showmigrations
python manage.py migrate --fake-initial

# 2. Dependency conflicts
# Problem: CircularDependencyError or cannot resolve dependencies
python manage.py makemigrations --merge
# Or manually edit migration dependencies

# 3. Database out of sync with migrations
# Problem: Table already exists error
python manage.py migrate --fake app_name migration_number

# 4. Reset migrations (DANGEROUS - development only)
python manage.py migrate app_name zero
rm app_name/migrations/0*.py
python manage.py makemigrations app_name
python manage.py migrate --fake-initial

# 5. Check migration consistency
python manage.py check
python manage.py migrate --plan

# 6. Manual state fixes (advanced)
python manage.py shell
>>> from django.db.migrations.recorder import MigrationRecorder
>>> recorder = MigrationRecorder(connection)
>>> recorder.migration_qs.filter(app='app_name').delete()
'''
    
    guide.print_solution([
        "# Common troubleshooting commands:",
        "python manage.py migrate --fake-initial  # Skip existing tables",
        "python manage.py makemigrations --merge   # Resolve conflicts",
        "python manage.py migrate --fake app 0002  # Mark as applied",
        "python manage.py check                    # Validate consistency",
        "",
        "# Emergency reset (development only):",
        "python manage.py migrate app zero",
        "rm app/migrations/0*.py",
        "python manage.py makemigrations app",
        "",
        "# Always backup before fixing!"
    ], "Know how to recover from migration issues safely")
    
    print(f"\n📋 TROUBLESHOOTING GUIDE:\n{troubleshooting_guide}")


def section_7_squashing_and_optimization(guide):
    """Section 7: Squashing and Migration Optimization"""
    guide.print_header("Squashing and Migration Optimization")
    
    print("""
🗜️ THEORY: Over time, applications accumulate many migration files:
• Hundreds of migrations slow down fresh installs
• Historical dependencies become complex
• Squashing combines multiple migrations into fewer files
• Optimization reduces redundant operations

SQUASHING PROCESS:
1. Combine sequential migrations
2. Optimize operation sequences  
3. Maintain compatibility with existing installations
4. Clean up after successful deployment
""")
    
    guide.print_header("Analyze Migration History", 2)
    guide.print_task("Review current migration count and complexity")
    guide.print_hint("Count migrations and identify squashing candidates")
    guide.wait_for_user()
    
    guide.print_solution([
        "# Count migrations per app:",
        "find . -name 'migrations' -type d -exec find {} -name '*.py' \\; | grep -v __init__ | wc -l",
        "",
        "# List all migrations:",
        "python manage.py showmigrations",
        "",
        "# Show migration plan:",
        "python manage.py showmigrations --plan",
        "",
        "# Identify squashing candidates:",
        "# - Apps with >10 migrations",
        "# - Sequential migrations without data operations"
    ], "Understanding migration history helps plan squashing strategy")
    
    # Count migrations
    success = guide.run_command("find . -name '*.py' -path '*/migrations/*' | grep -v __init__ | wc -l", 
                               "Counting migration files")
    
    guide.print_header("Perform Migration Squashing", 2)
    guide.print_task("Squash migrations to reduce complexity")
    guide.print_hint("Use squashmigrations command carefully")
    guide.wait_for_user()
    
    squashing_example = '''
# 1. Identify range to squash
python manage.py showmigrations blog

# 2. Create squashed migration
python manage.py squashmigrations blog 0001 0005
# This creates: 0001_squashed_0005_migration_name.py

# 3. Review the squashed migration
# Check that operations are optimized correctly

# 4. Test the squashed migration
# Apply on fresh database copy
python manage.py migrate --fake-initial

# 5. Deploy squashed migration
# Keep old migrations during transition period

# 6. Clean up after full deployment
# Remove old migration files
# Update dependencies in other apps
# Remove 'replaces' attribute from squashed migration
'''
    
    guide.print_solution([
        "# Basic squashing command:",
        "python manage.py squashmigrations app_name start_migration end_migration",
        "",
        "# Example:",
        "python manage.py squashmigrations blog 0001 0005",
        "",
        "# With custom name:",
        "python manage.py squashmigrations blog 0001 0005 --squashed-name initial_setup",
        "",
        "# Process:",
        "1. Create squashed migration",
        "2. Test thoroughly",
        "3. Deploy with old migrations",
        "4. Clean up after transition"
    ], "Squashing reduces migration complexity but requires careful deployment")
    
    print(f"\n📋 SQUASHING EXAMPLE:\n{squashing_example}")
    
    guide.print_header("Manual Migration Optimization", 2)
    guide.print_task("Manually optimize migration operations")
    guide.print_hint("Combine redundant operations, eliminate create/delete pairs")
    guide.wait_for_user()
    
    optimization_examples = '''
# Before optimization:
operations = [
    migrations.CreateModel('TempModel', fields=[...]),
    migrations.AddField('TempModel', 'field1', ...),
    migrations.AddField('TempModel', 'field2', ...),
    migrations.DeleteModel('TempModel'),  # Model created then deleted!
]

# After optimization:
operations = [
    # CreateModel + DeleteModel = no operation needed
]

# Before optimization:
operations = [
    migrations.AddField('Model', 'field1', ...),
    migrations.AlterField('Model', 'field1', ...),
    migrations.AlterField('Model', 'field1', ...),
]

# After optimization:
operations = [
    migrations.AddField('Model', 'field1', final_field_definition),
]

# Before optimization:
operations = [
    migrations.CreateModel('Model', fields=[...]),
    migrations.AddField('Model', 'new_field', ...),
]

# After optimization:
operations = [
    migrations.CreateModel('Model', fields=[
        # original fields +
        ('new_field', ...),  # Include new field in creation
    ]),
]
'''
    
    guide.print_solution([
        "# Common optimization patterns:",
        "1. CreateModel + DeleteModel = Remove both",
        "2. AddField + AlterField = Use final field definition",
        "3. CreateModel + AddField = Include field in CreateModel",
        "4. Multiple AlterField = Use final state only",
        "",
        "# Optimization rules:",
        "- Eliminate redundant operations",
        "- Combine related operations",
        "- Preserve data migrations",
        "- Test optimized results thoroughly"
    ], "Manual optimization can significantly reduce migration complexity")
    
    print(f"\n📋 OPTIMIZATION EXAMPLES:\n{optimization_examples}")


def main():
    """Main interactive practice session."""
    guide = MigrationsPracticeGuide()
    
    print("🚀 Django Migrations Interactive Practice Guide")
    print("Following: https://docs.djangoproject.com/en/5.2/topics/migrations/")
    print("="*80)
    print("""
🎯 LEARNING OBJECTIVES:
• Master all Django migration commands and workflows
• Create and manage schema migrations effectively
• Write safe and efficient data migrations
• Handle migration dependencies and conflicts
• Apply advanced migration techniques
• Implement migration best practices

📋 PRACTICE SECTIONS:
1. Migration Commands - Basic command mastery
2. Schema Migrations - Database structure changes
3. Data Migrations - Content transformation and seeding
4. Dependencies & Conflicts - Managing complex relationships
5. Advanced Operations - Custom SQL and operations
6. Best Practices - Testing, performance, troubleshooting
7. Squashing & Optimization - Managing migration complexity

💡 MIGRATION FUNDAMENTALS:
• Migrations = Version control for database schema
• makemigrations = Detect changes and create migration files
• migrate = Apply migrations to database
• Always review generated migrations before applying
• Test migrations thoroughly before production deployment

🔧 WORKFLOW:
   models.py changes → makemigrations → migrate → commit
   │                  │               │        │
   │                  │               │        └─ Version control
   │                  │               └─ Apply to database
   │                  └─ Generate migration files
   └─ Modify Django models

⚠️  CRITICAL SAFETY RULES:
• Always backup database before major migrations
• Test migrations on production-like data
• Plan rollback procedures for critical changes
• Use --dry-run to preview migration generation
• Review SQL with sqlmigrate before applying
""")
    
    choice = input("\n🚀 Ready to master Django Migrations? (y/n): ").lower()
    if choice != 'y':
        print("Come back when you're ready to explore Django's migration system! 🔄")
        return
    
    try:
        # Run all practice sections
        section_1_migration_commands(guide)
        section_2_schema_migrations(guide)
        section_3_data_migrations(guide)
        section_4_migration_dependencies(guide)
        section_5_advanced_operations(guide)
        section_6_migration_best_practices(guide)
        section_7_squashing_and_optimization(guide)
        
        print("\n" + "="*80)
        print("🎉 CONGRATULATIONS! Django Migrations Mastery Complete!")
        print("="*80)
        print("""
✅ YOU HAVE MASTERED:
• All Django migration commands (makemigrations, migrate, sqlmigrate, showmigrations)
• Schema migration patterns and best practices
• Data migration techniques with RunPython operations
• Migration dependency management and conflict resolution
• Advanced operations including custom SQL and non-atomic migrations
• Professional testing and deployment strategies
• Migration optimization and squashing techniques

🧠 KEY CONCEPTS LEARNED:
• Migration workflow and version control integration
• Forward and reverse migration operations
• Historical model usage in data migrations
• Cross-app dependencies and swappable models
• Performance considerations for large datasets
• Troubleshooting migration issues and state inconsistencies
• Production deployment strategies and rollback procedures

🔧 PRACTICAL SKILLS DEVELOPED:
• Writing safe and reversible data migrations
• Optimizing migrations for performance
• Handling complex dependency scenarios
• Creating custom migration operations
• Implementing comprehensive testing procedures
• Managing migration complexity with squashing

🚀 NEXT STEPS:
• Apply migration best practices to your projects
• Develop team workflows for migration management
• Create reusable custom migration operations
• Implement automated migration testing
• Master database-specific migration features

🏆 PROFESSIONAL MIGRATION MANAGEMENT:
You now have the skills to manage Django migrations in production environments with confidence. You understand the full lifecycle from development to deployment and can handle complex migration scenarios safely.

💡 Remember: Great migrations are boring migrations - they work reliably, perform well, and cause no surprises in production!
""")
        
    except KeyboardInterrupt:
        print("\n\n⏸️  Practice session interrupted. Resume anytime!")
    except Exception as e:
        print(f"\n❌ Error during practice: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
