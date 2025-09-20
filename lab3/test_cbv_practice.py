"""
Comprehensive test suite for Class-based Views Practice
Tests all major CBV patterns and functionality
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, date
from cbv_practice.models import Author, Category, Book, Article, Comment
import json


class CBVTestCase(TestCase):
    """Base test case with sample data"""
    
    def setUp(self):
        # Create test data
        self.category = Category.objects.create(
            name='Programming',
            slug='programming',
            description='Programming books and articles'
        )
        
        self.author = Author.objects.create(
            name='Test Author',
            email='test@example.com',
            bio='Test author biography',
            birth_date=date(1980, 1, 1)
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890123',
            pages=300,
            category=self.category,
            description='Test book description',
            price=29.99,
            publication_date=timezone.now().date(),
            is_available=True
        )
        self.book.authors.add(self.author)
        
        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            content='Test article content',
            author=self.author,
            category=self.category,
            is_published=True
        )
        
        self.client = Client()


class TemplateViewTests(CBVTestCase):
    """Test TemplateView implementations"""
    
    def test_home_view(self):
        """Test home page renders correctly"""
        response = self.client.get(reverse('cbv_practice:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Class-based Views Practice')
        self.assertContains(response, 'Recent Books')
        
    def test_about_view(self):
        """Test about page with context data"""
        response = self.client.get(reverse('cbv_practice:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About Our Library')
        self.assertContains(response, 'total_books')
        
    def test_stats_view(self):
        """Test statistics dashboard"""
        response = self.client.get(reverse('cbv_practice:stats'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Library Statistics')
        self.assertContains(response, '1')  # Should show 1 book


class BasicViewTests(CBVTestCase):
    """Test basic View class implementations"""
    
    def test_basic_view_get(self):
        """Test basic view GET method"""
        response = self.client.get(reverse('cbv_practice:basic-view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Basic Class-based View')
        
    def test_basic_view_post(self):
        """Test basic view POST method"""
        response = self.client.post(reverse('cbv_practice:basic-view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'POST Request Received')
        
    def test_json_response_view(self):
        """Test JSON response view"""
        response = self.client.get(reverse('cbv_practice:json-response'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertIn('message', data)
        self.assertIn('timestamp', data)


class RedirectViewTests(CBVTestCase):
    """Test RedirectView implementations"""
    
    def test_old_books_redirect(self):
        """Test permanent redirect"""
        response = self.client.get(reverse('cbv_practice:old-books-redirect'))
        self.assertEqual(response.status_code, 301)  # Permanent redirect
        
    def test_random_book_redirect(self):
        """Test random book redirect"""
        response = self.client.get(reverse('cbv_practice:random-book'))
        self.assertIn(response.status_code, [302, 301])  # Should redirect


class ListViewTests(CBVTestCase):
    """Test ListView implementations"""
    
    def test_book_list_view(self):
        """Test book list display"""
        response = self.client.get(reverse('cbv_practice:book-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)
        self.assertContains(response, 'Total found: 1')
        
    def test_book_list_search(self):
        """Test book list search functionality"""
        response = self.client.get(
            reverse('cbv_practice:book-list'),
            {'search': 'Test'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)
        
    def test_book_list_category_filter(self):
        """Test book list category filtering"""
        response = self.client.get(
            reverse('cbv_practice:book-list'),
            {'category': self.category.slug}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)
        
    def test_book_list_head_method(self):
        """Test HEAD method support"""
        response = self.client.head(reverse('cbv_practice:book-list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Last-Modified', response)
        
    def test_author_list_view(self):
        """Test author list with annotations"""
        response = self.client.get(reverse('cbv_practice:author-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.author.name)
        self.assertContains(response, 'Total Authors: 1')
        
    def test_article_list_view(self):
        """Test article list view"""
        response = self.client.get(reverse('cbv_practice:article-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)


class DetailViewTests(CBVTestCase):
    """Test DetailView implementations"""
    
    def test_book_detail_view(self):
        """Test book detail display"""
        response = self.client.get(
            reverse('cbv_practice:book-detail', kwargs={'pk': self.book.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)
        self.assertContains(response, self.book.description)
        
    def test_author_detail_view(self):
        """Test author detail with related objects"""
        response = self.client.get(
            reverse('cbv_practice:author-detail', kwargs={'pk': self.author.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.author.name)
        self.assertContains(response, self.author.bio)
        
    def test_article_detail_view(self):
        """Test article detail with view counting"""
        initial_views = self.article.views_count
        response = self.client.get(
            reverse('cbv_practice:article-detail', kwargs={'slug': self.article.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
        
        # Check view count incremented
        self.article.refresh_from_db()
        self.assertEqual(self.article.views_count, initial_views + 1)
        
    def test_category_detail_view(self):
        """Test category detail view"""
        response = self.client.get(
            reverse('cbv_practice:category-detail', kwargs={'slug': self.category.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.category.name)


class AsyncViewTests(CBVTestCase):
    """Test asynchronous view implementations"""
    
    def test_async_view(self):
        """Test basic async view"""
        response = self.client.get(reverse('cbv_practice:async-view'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertIn('message', data)
        self.assertIn('book_count', data)
        
    def test_async_stats_view(self):
        """Test complex async stats view"""
        response = self.client.get(reverse('cbv_practice:async-stats'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertIn('stats', data)
        self.assertIn('total_books', data['stats'])


class ErrorHandlingTests(CBVTestCase):
    """Test error handling in views"""
    
    def test_book_detail_404(self):
        """Test 404 for non-existent book"""
        response = self.client.get(
            reverse('cbv_practice:book-detail', kwargs={'pk': 99999})
        )
        self.assertEqual(response.status_code, 404)
        
    def test_article_detail_404(self):
        """Test 404 for non-existent article"""
        response = self.client.get(
            reverse('cbv_practice:article-detail', kwargs={'slug': 'non-existent'})
        )
        self.assertEqual(response.status_code, 404)


class URLPatternTests(CBVTestCase):
    """Test URL pattern resolution"""
    
    def test_all_url_patterns_resolve(self):
        """Test that all URL patterns resolve correctly"""
        url_names = [
            'cbv_practice:home',
            'cbv_practice:about',
            'cbv_practice:basic-view',
            'cbv_practice:json-response',
            'cbv_practice:book-list',
            'cbv_practice:author-list',
            'cbv_practice:article-list',
            'cbv_practice:stats',
            'cbv_practice:async-view',
            'cbv_practice:async-stats',
        ]
        
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                url = reverse(url_name)
                self.assertIsNotNone(url)
                
    def test_parameterized_urls(self):
        """Test URLs with parameters"""
        # Test with existing objects
        book_url = reverse('cbv_practice:book-detail', kwargs={'pk': self.book.pk})
        self.assertIn(str(self.book.pk), book_url)
        
        author_url = reverse('cbv_practice:author-detail', kwargs={'pk': self.author.pk})
        self.assertIn(str(self.author.pk), author_url)
        
        article_url = reverse('cbv_practice:article-detail', kwargs={'slug': self.article.slug})
        self.assertIn(self.article.slug, article_url)


class PaginationTests(CBVTestCase):
    """Test pagination functionality"""
    
    def setUp(self):
        super().setUp()
        # Create additional books for pagination testing
        for i in range(15):
            book = Book.objects.create(
                title=f'Book {i}',
                isbn=f'123456789012{i}',
                pages=300,
                category=self.category,
                description=f'Description for book {i}',
                price=19.99,
                publication_date=timezone.now().date(),
                is_available=True
            )
            book.authors.add(self.author)
            
    def test_book_list_pagination(self):
        """Test book list pagination"""
        response = self.client.get(reverse('cbv_practice:book-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'page=2')  # Should have page 2
        
    def test_pagination_page_2(self):
        """Test accessing page 2"""
        response = self.client.get(
            reverse('cbv_practice:book-list'),
            {'page': 2}
        )
        self.assertEqual(response.status_code, 200)


class PerformanceTests(CBVTestCase):
    """Test query optimization and performance"""
    
    def test_book_list_query_optimization(self):
        """Test that book list uses select_related"""
        with self.assertNumQueries(3):  # Should be minimal queries
            response = self.client.get(reverse('cbv_practice:book-list'))
            self.assertEqual(response.status_code, 200)
            
    def test_author_list_annotations(self):
        """Test author list annotations work correctly"""
        response = self.client.get(reverse('cbv_practice:author-list'))
        self.assertEqual(response.status_code, 200)
        
        # Check that annotations are present in context
        authors = response.context['authors']
        author = authors.first()
        self.assertTrue(hasattr(author, 'book_count'))
        self.assertTrue(hasattr(author, 'article_count'))
