"""
Data Cleanup Management Command
==============================

This demonstrates data cleanup operations with confirmation prompts.
Usage: python manage.py cleanup_data [--model MODEL] [--days N] [--dry-run]
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from model_class_practice.models import Article
import sys


class Command(BaseCommand):
    help = 'Clean up old or invalid data from the database'
    
    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument(
            '--model',
            choices=['articles', 'users', 'all'],
            default='articles',
            help='Which model to clean up (default: articles)'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete records older than N days (default: 30)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt'
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Process records in batches of N (default: 100)'
        )
    
    def handle(self, *args, **options):
        """Main command logic"""
        
        model = options['model']
        days = options['days']
        dry_run = options['dry_run']
        force = options['force']
        batch_size = options['batch_size']
        
        # Validate input
        if days < 0:
            raise CommandError('Days must be a non-negative integer')
        
        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f"Cleanup operation for: {model}")
        self.stdout.write(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write(f"Dry run mode: {dry_run}")
        self.stdout.write("-" * 50)
        
        # Perform cleanup based on model
        if model == 'articles':
            self.cleanup_articles(cutoff_date, dry_run, force, batch_size)
        elif model == 'users':
            self.cleanup_users(cutoff_date, dry_run, force, batch_size)
        elif model == 'all':
            self.cleanup_articles(cutoff_date, dry_run, force, batch_size)
            self.cleanup_users(cutoff_date, dry_run, force, batch_size)
    
    def cleanup_articles(self, cutoff_date, dry_run, force, batch_size):
        """Clean up old articles"""
        self.stdout.write("\\n" + self.style.HTTP_INFO("ARTICLES CLEANUP"))
        
        # Find articles to delete
        old_articles = Article.objects.filter(
            created__lt=cutoff_date,
            status='draft'  # Only delete draft articles
        )
        
        total_count = old_articles.count()
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS("No articles to cleanup"))
            return
        
        # Show what will be deleted
        self.stdout.write(f"Found {total_count} articles to delete:")
        
        # Show sample articles
        sample_articles = old_articles[:5]
        for article in sample_articles:
            self.stdout.write(
                f"  - {article.title} (Created: {article.created.strftime('%Y-%m-%d')})"
            )
        
        if total_count > 5:
            self.stdout.write(f"  ... and {total_count - 5} more")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: Would delete {total_count} articles")
            )
            return
        
        # Confirmation prompt
        if not force:
            confirm = input(f"\\nAre you sure you want to delete {total_count} articles? [y/N]: ")
            if confirm.lower() not in ['y', 'yes']:
                self.stdout.write("Operation cancelled")
                return
        
        # Delete in batches
        deleted_count = 0
        while True:
            batch = list(old_articles[:batch_size])
            if not batch:
                break
            
            # Delete batch
            batch_ids = [article.id for article in batch]
            Article.objects.filter(id__in=batch_ids).delete()
            
            deleted_count += len(batch)
            self.stdout.write(f"Deleted {deleted_count}/{total_count} articles...")
        
        self.stdout.write(
            self.style.SUCCESS(f"Successfully deleted {deleted_count} articles")
        )
    
    def cleanup_users(self, cutoff_date, dry_run, force, batch_size):
        """Clean up inactive users"""
        self.stdout.write("\\n" + self.style.HTTP_INFO("USERS CLEANUP"))
        
        # Find users to delete (inactive users with no articles)
        inactive_users = User.objects.filter(
            date_joined__lt=cutoff_date,
            is_active=False,
            last_login__isnull=True
        ).exclude(
            # Don't delete users who have articles
            article__isnull=False
        ).exclude(
            # Don't delete superusers
            is_superuser=True
        )
        
        total_count = inactive_users.count()
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS("No users to cleanup"))
            return
        
        # Show what will be deleted
        self.stdout.write(f"Found {total_count} inactive users to delete:")
        
        sample_users = inactive_users[:5]
        for user in sample_users:
            self.stdout.write(
                f"  - {user.username} (Joined: {user.date_joined.strftime('%Y-%m-%d')})"
            )
        
        if total_count > 5:
            self.stdout.write(f"  ... and {total_count - 5} more")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: Would delete {total_count} users")
            )
            return
        
        # Confirmation prompt
        if not force:
            confirm = input(f"\\nAre you sure you want to delete {total_count} users? [y/N]: ")
            if confirm.lower() not in ['y', 'yes']:
                self.stdout.write("Operation cancelled")
                return
        
        # Delete in batches
        deleted_count = 0
        while True:
            batch = list(inactive_users[:batch_size])
            if not batch:
                break
            
            batch_ids = [user.id for user in batch]
            User.objects.filter(id__in=batch_ids).delete()
            
            deleted_count += len(batch)
            self.stdout.write(f"Deleted {deleted_count}/{total_count} users...")
        
        self.stdout.write(
            self.style.SUCCESS(f"Successfully deleted {deleted_count} users")
        )
