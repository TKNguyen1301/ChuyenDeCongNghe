"""
Tests for Custom Management Commands
===================================

This file contains comprehensive tests for all custom management commands.
Run: python manage.py test model_class_practice.tests.test_commands
"""

from django.test import TestCase, TransactionTestCase
from django.core.management import call_command, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from io import StringIO
from unittest.mock import patch
from model_class_practice.models import Article
import json
import tempfile
import os


class CreateSampleDataCommandTest(TransactionTestCase):
    """Test the create_sample_data command"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_default_articles(self):
        """Test creating articles with default parameters"""
        call_command('create_sample_data', verbosity=0)
        
        # Should create 10 articles by default
        self.assertEqual(Article.objects.count(), 10)
        
        # All should be by admin user (created if not exists)
        admin_articles = Article.objects.filter(author__username='admin')
        self.assertEqual(admin_articles.count(), 10)
    
    def test_create_with_count(self):
        """Test creating specific number of articles"""
        call_command('create_sample_data', count=5, verbosity=0)
        self.assertEqual(Article.objects.count(), 5)
    
    def test_create_with_existing_author(self):
        """Test creating articles with existing author"""
        call_command('create_sample_data', 
                    count=3, 
                    author='testuser', 
                    verbosity=0)
        
        articles = Article.objects.filter(author=self.user)
        self.assertEqual(articles.count(), 3)
    
    def test_create_published_articles(self):
        """Test creating published articles"""
        call_command('create_sample_data', 
                    count=2, 
                    published=True, 
                    verbosity=0)
        
        published_articles = Article.objects.filter(is_published=True)
        self.assertEqual(published_articles.count(), 2)
    
    def test_invalid_count(self):
        """Test error handling for invalid count"""
        with self.assertRaises(CommandError):
            call_command('create_sample_data', count=0)
        
        with self.assertRaises(CommandError):
            call_command('create_sample_data', count=1001)
    
    def test_command_output(self):
        """Test command output messages"""
        out = StringIO()
        call_command('create_sample_data', 
                    count=2, 
                    verbosity=1,
                    stdout=out)
        
        output = out.getvalue()
        self.assertIn('Successfully created 2 articles', output)


class CleanupDataCommandTest(TransactionTestCase):
    """Test the cleanup_data command"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create old and new articles
        old_date = timezone.now() - timezone.timedelta(days=60)
        new_date = timezone.now()
        
        # Old draft article (should be deleted)
        self.old_draft = Article.objects.create(
            title='Old Draft',
            slug='old-draft',
            content='Old content',
            author=self.user,
            status='draft',
            created=old_date
        )
        
        # Old published article (should not be deleted)
        self.old_published = Article.objects.create(
            title='Old Published',
            slug='old-published',
            content='Old published content',
            author=self.user,
            status='published',
            is_published=True,
            created=old_date
        )
        
        # New draft article (should not be deleted)
        self.new_draft = Article.objects.create(
            title='New Draft',
            slug='new-draft',
            content='New content',
            author=self.user,
            status='draft',
            created=new_date
        )
    
    def test_dry_run_mode(self):
        """Test dry run mode doesn't delete anything"""
        initial_count = Article.objects.count()
        
        out = StringIO()
        call_command('cleanup_data', 
                    model='articles',
                    days=30,
                    dry_run=True,
                    verbosity=1,
                    stdout=out)
        
        # No articles should be deleted
        self.assertEqual(Article.objects.count(), initial_count)
        
        # Should show what would be deleted
        output = out.getvalue()
        self.assertIn('DRY RUN', output)
    
    def test_articles_cleanup_with_force(self):
        """Test cleaning up old draft articles with force flag"""
        call_command('cleanup_data',
                    model='articles',
                    days=30,
                    force=True,
                    verbosity=0)
        
        # Old draft should be deleted
        self.assertFalse(Article.objects.filter(id=self.old_draft.id).exists())
        
        # Others should remain
        self.assertTrue(Article.objects.filter(id=self.old_published.id).exists())
        self.assertTrue(Article.objects.filter(id=self.new_draft.id).exists())
    
    def test_no_cleanup_needed(self):
        """Test when no cleanup is needed"""
        # Delete the old draft manually
        self.old_draft.delete()
        
        out = StringIO()
        call_command('cleanup_data',
                    model='articles',
                    days=30,
                    verbosity=1,
                    stdout=out)
        
        output = out.getvalue()
        self.assertIn('No articles to cleanup', output)


class DbStatsCommandTest(TestCase):
    """Test the db_stats command"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create some test articles
        Article.objects.create(
            title='Test Article 1',
            slug='test-article-1',
            content='Test content',
            author=self.user,
            view_count=100
        )
        
        Article.objects.create(
            title='Test Article 2',
            slug='test-article-2',
            content='Test content',
            author=self.user,
            is_published=True,
            view_count=200
        )
    
    def test_table_format_output(self):
        """Test table format output"""
        out = StringIO()
        call_command('db_stats', 
                    format='table',
                    verbosity=0,
                    stdout=out)
        
        output = out.getvalue()
        self.assertIn('DATABASE STATISTICS REPORT', output)
        self.assertIn('USERS', output)
        self.assertIn('ARTICLES', output)
        self.assertIn('Total Users:', output)
        self.assertIn('Total Articles:', output)
    
    def test_json_format_output(self):
        """Test JSON format output"""
        out = StringIO()
        call_command('db_stats',
                    format='json',
                    verbosity=0,
                    stdout=out)
        
        output = out.getvalue()
        
        # Should be valid JSON
        try:
            data = json.loads(output)
            self.assertIn('users', data)
            self.assertIn('articles', data)
            self.assertIn('generated_at', data)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")
    
    def test_csv_format_output(self):
        """Test CSV format output"""
        out = StringIO()
        call_command('db_stats',
                    format='csv',
                    verbosity=0,
                    stdout=out)
        
        output = out.getvalue()
        lines = output.strip().split('\\n')
        
        # Should have header
        self.assertEqual(lines[0], 'metric,value')
        
        # Should have data lines
        self.assertTrue(any('total_users' in line for line in lines))
        self.assertTrue(any('total_articles' in line for line in lines))
    
    def test_export_to_file(self):
        """Test exporting to file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            out = StringIO()
            call_command('db_stats',
                        format='json',
                        export=temp_filename,
                        verbosity=1,
                        stdout=out)
            
            # Check file was created
            self.assertTrue(os.path.exists(temp_filename))
            
            # Check file contents
            with open(temp_filename, 'r') as f:
                content = f.read()
                data = json.loads(content)
                self.assertIn('users', data)
                self.assertIn('articles', data)
            
            # Check command output
            output = out.getvalue()
            self.assertIn(f'exported to {temp_filename}', output)
            
        finally:
            # Cleanup
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


class ProcessArticlesCommandTest(TestCase):
    """Test the process_articles command"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            content='Test content',
            author=self.user,
            status='draft'
        )
    
    def test_show_article_info(self):
        """Test showing article information"""
        out = StringIO()
        call_command('process_articles',
                    str(self.article.id),
                    action='info',
                    verbosity=0,
                    stdout=out)
        
        output = out.getvalue()
        self.assertIn('Article Information:', output)
        self.assertIn(f'ID: {self.article.id}', output)
        self.assertIn(f'Title: {self.article.title}', output)
    
    def test_publish_article(self):
        """Test publishing an article"""
        out = StringIO()
        call_command('process_articles',
                    str(self.article.id),
                    action='publish',
                    verbosity=0,
                    stdout=out)
        
        # Refresh from database
        self.article.refresh_from_db()
        
        self.assertTrue(self.article.is_published)
        self.assertEqual(self.article.status, 'published')
        self.assertIsNotNone(self.article.published_date)
        
        output = out.getvalue()
        self.assertIn('Published article:', output)
    
    def test_process_by_slug(self):
        """Test processing article by slug"""
        out = StringIO()
        call_command('process_articles',
                    self.article.slug,
                    action='info',
                    verbosity=0,
                    stdout=out)
        
        output = out.getvalue()
        self.assertIn(f'Title: {self.article.title}', output)
    
    def test_nonexistent_article(self):
        """Test processing nonexistent article"""
        err = StringIO()
        call_command('process_articles',
                    '999',
                    action='info',
                    verbosity=0,
                    stderr=err)
        
        error_output = err.getvalue()
        self.assertIn('Article not found: 999', error_output)


class AppMaintenanceCommandTest(TestCase):
    """Test the app_maintenance command"""
    
    def test_app_info_operation(self):
        """Test app info operation"""
        out = StringIO()
        call_command('app_maintenance',
                    'model_class_practice',
                    operation='info',
                    verbosity=0,
                    stdout=out)
        
        output = out.getvalue()
        self.assertIn('APP: model_class_practice', output)
        self.assertIn('Name:', output)
        self.assertIn('Models:', output)
    
    def test_models_operation(self):
        """Test models operation"""
        out = StringIO()
        call_command('app_maintenance',
                    'model_class_practice',
                    operation='models',
                    verbosity=0,
                    stdout=out)
        
        output = out.getvalue()
        self.assertIn('Models (', output)
        self.assertIn('Article', output)
    
    def test_data_summary_operation(self):
        """Test data summary operation"""
        # Create some test data
        user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        Article.objects.create(
            title='Test',
            slug='test',
            content='Content',
            author=user
        )
        
        out = StringIO()
        call_command('app_maintenance',
                    'model_class_practice',
                    operation='data-summary',
                    verbosity=0,
                    stdout=out)
        
        output = out.getvalue()
        self.assertIn('Data Summary:', output)
        self.assertIn('Article', output)
        self.assertIn('records', output)


class CommandIntegrationTest(TransactionTestCase):
    """Integration tests for command workflows"""
    
    def test_complete_workflow(self):
        """Test a complete workflow using multiple commands"""
        
        # 1. Create sample data
        call_command('create_sample_data', count=5, verbosity=0)
        self.assertEqual(Article.objects.count(), 5)
        
        # 2. Get statistics
        out = StringIO()
        call_command('db_stats', format='json', verbosity=0, stdout=out)
        stats = json.loads(out.getvalue())
        self.assertEqual(stats['articles']['total'], 5)
        
        # 3. Process articles
        articles = Article.objects.all()[:2]
        for article in articles:
            call_command('process_articles', 
                        str(article.id), 
                        action='publish', 
                        verbosity=0)
        
        # Verify published articles
        published_count = Article.objects.filter(is_published=True).count()
        self.assertEqual(published_count, 2)
        
        # 4. Cleanup old data (dry run)
        out = StringIO()
        call_command('cleanup_data', 
                    model='articles',
                    days=1,  # Everything should be "old"
                    dry_run=True,
                    verbosity=0,
                    stdout=out)
        
        # Articles should still exist after dry run
        self.assertEqual(Article.objects.count(), 5)
