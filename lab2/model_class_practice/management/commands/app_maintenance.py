"""
AppCommand Example - Process Applications
========================================

This demonstrates AppCommand for processing Django applications.
Usage: python manage.py app_maintenance auth contenttypes model_class_practice
"""

from django.core.management.base import AppCommand
from django.apps import apps
from django.db import models


class Command(AppCommand):
    help = 'Perform maintenance operations on Django applications'
    
    def add_arguments(self, parser):
        """Add command arguments"""
        super().add_arguments(parser)
        
        parser.add_argument(
            '--operation',
            choices=['info', 'models', 'migration-status', 'data-summary'],
            default='info',
            help='Operation to perform (default: info)'
        )
        
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed information'
        )
    
    def handle_app_config(self, app_config, **options):
        """Process a single app config"""
        
        operation = options['operation']
        detailed = options['detailed']
        
        self.stdout.write(f"\\n{'='*60}")
        self.stdout.write(f"APP: {app_config.label}")
        self.stdout.write(f"{'='*60}")
        
        if operation == 'info':
            self.show_app_info(app_config, detailed)
        elif operation == 'models':
            self.show_models_info(app_config, detailed)
        elif operation == 'migration-status':
            self.show_migration_status(app_config)
        elif operation == 'data-summary':
            self.show_data_summary(app_config)
    
    def show_app_info(self, app_config, detailed):
        """Show basic app information"""
        self.stdout.write(f"Name: {app_config.name}")
        self.stdout.write(f"Label: {app_config.label}")
        self.stdout.write(f"Path: {app_config.path}")
        self.stdout.write(f"Models: {len(app_config.get_models())}")
        
        if detailed:
            self.stdout.write(f"Module: {app_config.module}")
            self.stdout.write(f"Verbose Name: {getattr(app_config, 'verbose_name', 'N/A')}")
    
    def show_models_info(self, app_config, detailed):
        """Show models information"""
        models_list = app_config.get_models()
        
        self.stdout.write(f"Models ({len(models_list)}):")
        self.stdout.write("-" * 30)
        
        for model in models_list:
            self.stdout.write(f"  {model.__name__}")
            
            if detailed:
                # Show field count
                field_count = len(model._meta.get_fields())
                self.stdout.write(f"    Fields: {field_count}")
                
                # Show table name
                self.stdout.write(f"    Table: {model._meta.db_table}")
                
                # Show record count (if possible)
                try:
                    count = model.objects.count()
                    self.stdout.write(f"    Records: {count:,}")
                except Exception as e:
                    self.stdout.write(f"    Records: Error - {e}")
    
    def show_migration_status(self, app_config):
        """Show migration status for the app"""
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection
        
        try:
            executor = MigrationExecutor(connection)
            migrations = executor.loader.graph.migrations
            
            app_migrations = [
                migration for migration in migrations 
                if migration[0] == app_config.label
            ]
            
            self.stdout.write(f"Migrations ({len(app_migrations)}):")
            self.stdout.write("-" * 30)
            
            if not app_migrations:
                self.stdout.write("  No migrations found")
                return
            
            # Check applied status
            applied_migrations = executor.loader.applied_migrations
            
            for migration_key in sorted(app_migrations):
                migration = migrations[migration_key]
                status = "✓ Applied" if migration_key in applied_migrations else "✗ Pending"
                self.stdout.write(f"  {migration_key[1]:30} {status}")
                
        except Exception as e:
            self.stderr.write(f"Error checking migrations: {e}")
    
    def show_data_summary(self, app_config):
        """Show data summary for the app"""
        models_list = app_config.get_models()
        total_records = 0
        
        self.stdout.write("Data Summary:")
        self.stdout.write("-" * 30)
        
        for model in models_list:
            try:
                count = model.objects.count()
                total_records += count
                self.stdout.write(f"  {model.__name__:20} {count:>8,} records")
                
                # Show recent activity if model has date field
                if hasattr(model, 'created'):
                    from django.utils import timezone
                    from datetime import timedelta
                    
                    recent_count = model.objects.filter(
                        created__gte=timezone.now() - timedelta(days=7)
                    ).count()
                    if recent_count > 0:
                        self.stdout.write(f"    (↑ {recent_count} in last 7 days)")
                        
            except Exception as e:
                self.stdout.write(f"  {model.__name__:20} Error: {e}")
        
        self.stdout.write("-" * 30)
        self.stdout.write(f"  {'TOTAL':20} {total_records:>8,} records")
