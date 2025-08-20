"""
Django Custom Management Commands - Practice Guide
=================================================

This script demonstrates how to use and test custom management commands.
Run: python custom_commands_practice.py
"""

import os
import sys
import django


def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modelspractice.settings')
    django.setup()


def demonstrate_commands():
    """Demonstrate various custom management commands"""
    print("=" * 60)
    print("DJANGO CUSTOM MANAGEMENT COMMANDS PRACTICE")
    print("=" * 60)
    
    # Basic usage examples
    basic_commands = {
        "Data Creation": [
            "python manage.py create_sample_data",
            "python manage.py create_sample_data --count 20",
            "python manage.py create_sample_data --count 5 --author admin --published",
            "python manage.py create_sample_data --count 3 --status published --tags django python web"
        ],
        
        "Data Cleanup": [
            "python manage.py cleanup_data --dry-run",
            "python manage.py cleanup_data --model articles --days 30",
            "python manage.py cleanup_data --model users --days 90 --force",
            "python manage.py cleanup_data --model all --batch-size 50"
        ],
        
        "Statistics & Reports": [
            "python manage.py db_stats",
            "python manage.py db_stats --format json",
            "python manage.py db_stats --include-details",
            "python manage.py db_stats --export report.json --format json"
        ],
        
        "Article Processing": [
            "python manage.py process_articles 1 2 3 --action info",
            "python manage.py process_articles article-slug --action publish", 
            "python manage.py process_articles 1 --action delete --force"
        ],
        
        "App Maintenance": [
            "python manage.py app_maintenance model_class_practice",
            "python manage.py app_maintenance auth contenttypes --operation models",
            "python manage.py app_maintenance model_class_practice --operation data-summary --detailed"
        ]
    }
    
    for category, commands in basic_commands.items():
        print(f"\\n{category}:")
        print("-" * len(category))
        for cmd in commands:
            print(f"  {cmd}")
    
    # Advanced usage patterns
    print("\\n" + "=" * 60)
    print("ADVANCED USAGE PATTERNS")
    print("=" * 60)
    
    advanced_patterns = """
1. CHAINING COMMANDS:
   python manage.py create_sample_data --count 50 && python manage.py db_stats

2. SCRIPTED OPERATIONS:
   #!/bin/bash
   # Daily maintenance script
   python manage.py cleanup_data --days 30 --force
   python manage.py db_stats --export daily_report.json --format json

3. CONDITIONAL EXECUTION:
   python manage.py db_stats --format json | jq '.articles.total' | \\
   xargs -I {} python manage.py create_sample_data --count {}

4. BACKGROUND PROCESSING:
   nohup python manage.py cleanup_data --model all --days 90 > cleanup.log 2>&1 &

5. CRON JOBS:
   # Daily at 2 AM - cleanup old data
   0 2 * * * cd /path/to/project && python manage.py cleanup_data --days 30 --force

   # Weekly reports
   0 8 * * 1 cd /path/to/project && python manage.py db_stats --export weekly_report.json
"""
    
    print(advanced_patterns)


def show_command_structure():
    """Show the structure of custom commands"""
    print("\\n" + "=" * 60)
    print("COMMAND STRUCTURE REFERENCE")
    print("=" * 60)
    
    structure = """
PROJECT STRUCTURE:
==================
your_app/
    management/
        __init__.py
        commands/
            __init__.py
            your_command.py      # BaseCommand
            app_command.py       # AppCommand
            label_command.py     # LabelCommand

BASECOMMAND TEMPLATE:
====================
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Command description'
    
    def add_arguments(self, parser):
        parser.add_argument('--option', help='Option description')
    
    def handle(self, *args, **options):
        # Command logic here
        self.stdout.write(self.style.SUCCESS('Success message'))

COMMAND ATTRIBUTES:
==================
• help: Help text for the command
• output_transaction: Wrap with BEGIN/COMMIT
• requires_migrations_checks: Check migrations
• requires_system_checks: Run system checks
• style: Colored output styling

ARGUMENT TYPES:
===============
• Positional: parser.add_argument('name')
• Optional: parser.add_argument('--name')
• Boolean: parser.add_argument('--flag', action='store_true')
• Choices: parser.add_argument('--type', choices=['a', 'b'])
• Multiple: parser.add_argument('--items', nargs='*')

OUTPUT METHODS:
===============
• self.stdout.write(): Normal output
• self.stderr.write(): Error output
• self.style.SUCCESS(): Green success message
• self.style.ERROR(): Red error message
• self.style.WARNING(): Yellow warning
• self.style.HTTP_INFO(): Blue info message

ERROR HANDLING:
===============
• raise CommandError('message'): Graceful error
• Use try/except for database operations
• Validate arguments before processing
• Provide helpful error messages
"""
    
    print(structure)


def show_testing_guide():
    """Show how to test custom commands"""
    print("\\n" + "=" * 60)
    print("TESTING CUSTOM COMMANDS")
    print("=" * 60)
    
    testing_guide = """
TESTING COMMANDS:
=================

1. UNIT TESTING:
   from django.test import TestCase
   from django.core.management import call_command
   from io import StringIO
   
   class CommandTestCase(TestCase):
       def test_command(self):
           out = StringIO()
           call_command('your_command', stdout=out)
           self.assertIn('expected output', out.getvalue())

2. INTEGRATION TESTING:
   from django.test import TransactionTestCase
   from django.core.management import call_command
   
   class IntegrationTestCase(TransactionTestCase):
       def test_data_creation(self):
           call_command('create_sample_data', count=5)
           self.assertEqual(Article.objects.count(), 5)

3. MOCKING EXTERNAL DEPENDENCIES:
   from unittest.mock import patch
   
   @patch('your_app.external_service')
   def test_with_mock(self, mock_service):
       call_command('your_command')
       mock_service.assert_called_once()

4. TESTING WITH ARGUMENTS:
   call_command('your_command', 
                arg1='value1',
                option1='value2',
                verbosity=2)

5. TESTING OUTPUT:
   from django.test import TestCase
   from django.core.management import call_command
   from io import StringIO
   
   def test_output(self):
       out = StringIO()
       err = StringIO()
       call_command('command', stdout=out, stderr=err)
       
       self.assertIn('success', out.getvalue())
       self.assertEqual('', err.getvalue())

6. TESTING EXCEPTIONS:
   with self.assertRaises(CommandError):
       call_command('command', invalid_arg='value')
"""
    
    print(testing_guide)


def show_best_practices():
    """Show best practices for custom commands"""
    print("\\n" + "=" * 60)
    print("BEST PRACTICES")
    print("=" * 60)
    
    practices = """
DESIGN PRINCIPLES:
==================
1. Single Responsibility: One command, one purpose
2. Idempotent Operations: Safe to run multiple times
3. Graceful Error Handling: Clear error messages
4. Progress Indicators: For long-running operations
5. Dry-run Options: Preview changes before applying

PERFORMANCE:
============
1. Use bulk operations for large datasets
2. Process data in batches
3. Use select_related() and prefetch_related()
4. Consider database indexes for queries
5. Monitor memory usage for large operations

SECURITY:
=========
1. Validate all input arguments
2. Use transactions for data modifications
3. Don't expose sensitive information in output
4. Log security-relevant operations
5. Consider rate limiting for API calls

USABILITY:
==========
1. Provide helpful help text
2. Use consistent argument naming
3. Support different output formats
4. Include progress indicators
5. Provide detailed error messages

MAINTENANCE:
============
1. Write comprehensive tests
2. Document command usage
3. Version your commands
4. Handle backward compatibility
5. Monitor command performance
"""
    
    print(practices)


def main():
    """Main execution function"""
    try:
        setup_django()
        demonstrate_commands()
        show_command_structure()
        show_testing_guide()
        show_best_practices()
        
        print("\\n" + "=" * 60)
        print("NEXT STEPS:")
        print("1. Test the custom commands we created")
        print("2. Create your own custom commands")
        print("3. Write unit tests for commands")
        print("4. Set up scheduled tasks using cron")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you're in the correct Django project directory")


if __name__ == "__main__":
    main()
