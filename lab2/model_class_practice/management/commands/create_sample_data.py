"""
Basic Custom Management Command Example
=====================================

This demonstrates a simple BaseCommand implementation for data management.
Usage: python manage.py create_sample_data [--count N] [--category CATEGORY]
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from model_class_practice.models import Article
from django.utils import timezone
from django.utils.text import slugify
import random


class Command(BaseCommand):
    help = 'Create sample articles for testing purposes'
    
    def add_arguments(self, parser):
        """Add command arguments"""
        # Positional argument
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of articles to create (default: 10)'
        )
        
        # Named optional argument
        parser.add_argument(
            '--author',
            type=str,
            help='Username of the author (will create if not exists)'
        )
        
        # Boolean flag
        parser.add_argument(
            '--published',
            action='store_true',
            help='Create articles as published'
        )
        
        # Choice argument
        parser.add_argument(
            '--status',
            choices=['draft', 'review', 'published', 'archived'],
            default='draft',
            help='Status of created articles'
        )
        
        # Multiple values
        parser.add_argument(
            '--tags',
            nargs='*',
            help='Tags to add to articles'
        )
    
    def handle(self, *args, **options):
        """Main command logic"""
        
        # Get command options
        count = options['count']
        author_username = options['author'] or 'admin'
        is_published = options['published']
        status = options['status']
        tags = options.get('tags', [])
        
        # Validate count
        if count <= 0:
            raise CommandError('Count must be a positive integer')
        
        if count > 1000:
            raise CommandError('Cannot create more than 1000 articles at once')
        
        # Get or create author
        try:
            author = User.objects.get(username=author_username)
            self.stdout.write(f"Using existing author: {author.username}")
        except User.DoesNotExist:
            if options['verbosity'] >= 2:
                self.stdout.write(f"Creating new user: {author_username}")
            author = User.objects.create_user(
                username=author_username,
                email=f"{author_username}@example.com",
                password="defaultpass123"
            )
            self.stdout.write(
                self.style.SUCCESS(f"Created new author: {author.username}")
            )
        
        # Sample content
        sample_titles = [
            "Introduction to Django",
            "Advanced Python Techniques", 
            "Web Development Best Practices",
            "Database Optimization Tips",
            "API Design Patterns",
            "Testing Strategies",
            "Deployment Automation",
            "Performance Monitoring",
            "Security Considerations",
            "Scaling Applications"
        ]
        
        sample_content = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod 
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, 
        quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo 
        consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse 
        cillum dolore eu fugiat nulla pariatur.
        """
        
        # Progress tracking
        created_articles = []
        failed_articles = 0
        
        # Create articles
        for i in range(count):
            try:
                # Generate article data
                base_title = random.choice(sample_titles)
                title = f"{base_title} - Part {i+1}"
                slug = slugify(title)
                
                # Ensure unique slug
                counter = 1
                original_slug = slug
                while Article.objects.filter(slug=slug).exists():
                    slug = f"{original_slug}-{counter}"
                    counter += 1
                
                # Create article
                article = Article.objects.create(
                    title=title,
                    slug=slug,
                    content=sample_content + f"\\n\\nThis is article number {i+1}.",
                    author=author,
                    status=status,
                    is_published=is_published,
                    published_date=timezone.now() if is_published else None,
                    view_count=random.randint(0, 1000)
                )
                
                created_articles.append(article)
                
                # Progress indicator
                if options['verbosity'] >= 2:
                    self.stdout.write(f"Created article: {article.title}")
                elif i % 10 == 9:  # Show progress every 10 articles
                    self.stdout.write(f"Created {i+1}/{count} articles...")
                    
            except Exception as e:
                failed_articles += 1
                if options['verbosity'] >= 1:
                    self.stderr.write(
                        self.style.ERROR(f"Failed to create article {i+1}: {e}")
                    )
        
        # Summary
        success_count = len(created_articles)
        self.stdout.write("\\n" + "="*50)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {success_count} articles"
            )
        )
        
        if failed_articles > 0:
            self.stdout.write(
                self.style.WARNING(f"Failed to create {failed_articles} articles")
            )
        
        # Additional info with high verbosity
        if options['verbosity'] >= 2:
            self.stdout.write("\\nCreated articles:")
            for article in created_articles[:5]:  # Show first 5
                self.stdout.write(f"  - {article.title} (ID: {article.id})")
            if len(created_articles) > 5:
                self.stdout.write(f"  ... and {len(created_articles) - 5} more")
        
        # Return summary for testing
        return f"Created {success_count} articles, {failed_articles} failed"
