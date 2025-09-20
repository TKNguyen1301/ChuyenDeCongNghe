"""
LabelCommand Example - Process Multiple Labels
=============================================

This demonstrates LabelCommand for processing multiple items.
Usage: python manage.py process_articles article1 article2 article3 [--action publish]
"""

from django.core.management.base import LabelCommand, CommandError
from model_class_practice.models import Article
from django.utils import timezone


class Command(LabelCommand):
    help = 'Process multiple articles by ID or slug'
    label = 'article_identifier'
    
    def add_arguments(self, parser):
        """Add command arguments"""
        super().add_arguments(parser)
        
        parser.add_argument(
            '--action',
            choices=['publish', 'unpublish', 'archive', 'delete', 'info'],
            default='info',
            help='Action to perform on articles (default: info)'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation for destructive actions'
        )
    
    def handle_label(self, label, **options):
        """Process a single article label"""
        
        action = options['action']
        force = options['force']
        
        # Find article by ID or slug
        article = self.get_article(label)
        
        if not article:
            self.stderr.write(
                self.style.ERROR(f"Article not found: {label}")
            )
            return
        
        # Perform action
        if action == 'info':
            self.show_article_info(article)
        elif action == 'publish':
            self.publish_article(article)
        elif action == 'unpublish':
            self.unpublish_article(article)
        elif action == 'archive':
            self.archive_article(article)
        elif action == 'delete':
            self.delete_article(article, force)
    
    def get_article(self, identifier):
        """Get article by ID or slug"""
        try:
            # Try to get by ID first
            if identifier.isdigit():
                return Article.objects.get(id=int(identifier))
            else:
                # Try to get by slug
                return Article.objects.get(slug=identifier)
        except Article.DoesNotExist:
            return None
    
    def show_article_info(self, article):
        """Display article information"""
        self.stdout.write(f"\\nArticle Information:")
        self.stdout.write(f"ID: {article.id}")
        self.stdout.write(f"Title: {article.title}")
        self.stdout.write(f"Slug: {article.slug}")
        self.stdout.write(f"Author: {article.author.username}")
        self.stdout.write(f"Status: {article.status}")
        self.stdout.write(f"Published: {article.is_published}")
        self.stdout.write(f"Created: {article.created}")
        self.stdout.write(f"Views: {article.view_count}")
    
    def publish_article(self, article):
        """Publish an article"""
        if article.is_published:
            self.stdout.write(
                self.style.WARNING(f"Article '{article.title}' is already published")
            )
            return
        
        article.is_published = True
        article.status = 'published'
        article.published_date = timezone.now()
        article.save()
        
        self.stdout.write(
            self.style.SUCCESS(f"Published article: '{article.title}'")
        )
    
    def unpublish_article(self, article):
        """Unpublish an article"""
        if not article.is_published:
            self.stdout.write(
                self.style.WARNING(f"Article '{article.title}' is not published")
            )
            return
        
        article.is_published = False
        article.status = 'draft'
        article.published_date = None
        article.save()
        
        self.stdout.write(
            self.style.SUCCESS(f"Unpublished article: '{article.title}'")
        )
    
    def archive_article(self, article):
        """Archive an article"""
        if article.status == 'archived':
            self.stdout.write(
                self.style.WARNING(f"Article '{article.title}' is already archived")
            )
            return
        
        article.status = 'archived'
        article.is_published = False
        article.save()
        
        self.stdout.write(
            self.style.SUCCESS(f"Archived article: '{article.title}'")
        )
    
    def delete_article(self, article, force):
        """Delete an article"""
        
        if not force:
            confirm = input(f"Are you sure you want to delete '{article.title}'? [y/N]: ")
            if confirm.lower() not in ['y', 'yes']:
                self.stdout.write("Deletion cancelled")
                return
        
        title = article.title
        article.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f"Deleted article: '{title}'")
        )
