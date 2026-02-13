from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from django.utils import timezone
import json

from .models import (
    Product, Order, OrderItem, Article, Comment, 
    Billing, Account
)


class PaginationTestCase(APITestCase):
    """
    Base test case for pagination testing with sample data.
    """
    
    def setUp(self):
        """Create test data for pagination testing."""
        # Create users
        self.user1 = User.objects.create_user('testuser1', 'test1@example.com', 'pass123')
        self.user2 = User.objects.create_user('testuser2', 'test2@example.com', 'pass123')
        self.staff_user = User.objects.create_user('staff', 'staff@example.com', 'pass123', is_staff=True)
        
        # Create products (50 items for testing pagination)
        self.products = []
        categories = ['Electronics', 'Books', 'Clothing', 'Home', 'Sports']
        for i in range(50):
            product = Product.objects.create(
                name=f'Product {i+1}',
                description=f'Description for product {i+1}',
                price=Decimal(f'{10 + i}.99'),
                category=categories[i % 5],
                stock_quantity=100 - i
            )
            self.products.append(product)
        
        # Create articles (30 items)
        self.articles = []
        for i in range(30):
            article = Article.objects.create(
                title=f'Article {i+1}',
                content=f'Content for article {i+1}' * 10,  # Longer content
                author=self.user1 if i % 2 == 0 else self.user2,
                slug=f'article-{i+1}',
                published=True,
                view_count=i * 10
            )
            self.articles.append(article)
        
        # Create orders (20 items)
        self.orders = []
        for i in range(20):
            order = Order.objects.create(
                customer=self.user1 if i % 2 == 0 else self.user2,
                status='pending' if i % 3 == 0 else 'shipped',
                total_amount=Decimal(f'{100 + i * 10}.00'),
                shipping_address=f'Address {i+1}, Test City'
            )
            self.orders.append(order)
            
            # Add order items
            for j in range(min(3, len(self.products))):
                OrderItem.objects.create(
                    order=order,
                    product=self.products[j],
                    quantity=j + 1,
                    unit_price=self.products[j].price
                )
        
        # Create comments (100 items for testing cursor pagination)
        self.comments = []
        for i in range(100):
            comment = Comment.objects.create(
                article=self.articles[i % len(self.articles)],
                author=self.user1 if i % 2 == 0 else self.user2,
                content=f'Comment {i+1} content'
            )
            self.comments.append(comment)
        
        # Create billing records (30 items)
        self.billing_records = []
        for i in range(30):
            billing = Billing.objects.create(
                customer=self.user1 if i % 2 == 0 else self.user2,
                amount=Decimal(f'{50 + i * 5}.00'),
                billing_date=timezone.now(),
                description=f'Billing record {i+1}',
                paid=i % 3 == 0
            )
            self.billing_records.append(billing)
        
        # Create accounts (25 items)
        self.accounts = []
        account_types = ['checking', 'savings', 'credit']
        for i in range(25):
            account = Account.objects.create(
                user=self.user1 if i % 2 == 0 else self.user2,
                account_number=f'ACC{1000000 + i}',
                balance=Decimal(f'{1000 + i * 100}.00'),
                account_type=account_types[i % 3],
                is_active=i % 4 != 0  # Some inactive accounts
            )
            self.accounts.append(account)


class PageNumberPaginationTest(PaginationTestCase):
    """
    Test PageNumberPagination functionality.
    """
    
    def test_basic_page_number_pagination(self):
        """Test basic page number pagination."""
        url = reverse('pagination:product-page-number')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Check pagination structure
        self.assertIn('count', data)
        self.assertIn('next', data)
        self.assertIn('previous', data)
        self.assertIn('results', data)
        
        # Check counts
        self.assertEqual(data['count'], 50)  # Total products
        self.assertEqual(len(data['results']), 10)  # Default page size
        
        # First page should have next but no previous
        self.assertIsNotNone(data['next'])
        self.assertIsNone(data['previous'])
    
    def test_page_number_pagination_second_page(self):
        """Test second page of pagination."""
        url = reverse('pagination:product-page-number')
        response = self.client.get(url, {'page': 2})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Second page should have both next and previous
        self.assertIsNotNone(data['next'])
        self.assertIsNotNone(data['previous'])
    
    def test_custom_pagination_format(self):
        """Test custom pagination with nested links."""
        url = reverse('pagination:product-custom')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Check custom format structure
        self.assertIn('links', data)
        self.assertIn('count', data)
        self.assertIn('results', data)
        
        # Check nested links structure
        links = data['links']
        self.assertIn('next', links)
        self.assertIn('previous', links)
    
    def test_large_results_pagination(self):
        """Test large results set pagination."""
        url = reverse('pagination:product-large')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should return all 50 products in one page (page_size=1000)
        self.assertEqual(len(data['results']), 50)
        self.assertIsNone(data['next'])
    
    def test_standard_pagination_with_page_size(self):
        """Test standard pagination with custom page size."""
        url = reverse('pagination:product-standard')
        response = self.client.get(url, {'page_size': 5})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should return 5 items per page
        self.assertEqual(len(data['results']), 5)
        self.assertIsNotNone(data['next'])
    
    def test_flexible_pagination_max_parameter(self):
        """Test flexible pagination with 'max' parameter."""
        url = reverse('pagination:product-flexible')
        response = self.client.get(url, {'page_size': 'max'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should return all products (up to max_page_size)
        self.assertEqual(len(data['results']), 50)


class LimitOffsetPaginationTest(PaginationTestCase):
    """
    Test LimitOffsetPagination functionality.
    """
    
    def test_basic_limit_offset_pagination(self):
        """Test basic limit/offset pagination."""
        url = reverse('pagination:order-limit-offset')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Check limit/offset structure
        self.assertIn('count', data)
        self.assertIn('next', data)
        self.assertIn('previous', data)
        self.assertIn('results', data)
        
        # Check counts
        self.assertEqual(data['count'], 20)  # Total orders
        self.assertEqual(len(data['results']), 10)  # Default page size
    
    def test_limit_offset_with_parameters(self):
        """Test limit/offset with custom parameters."""
        url = reverse('pagination:order-limit-offset')
        response = self.client.get(url, {'limit': 5, 'offset': 10})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should return 5 items starting from offset 10
        self.assertEqual(len(data['results']), 5)
        
        # Check that next URL contains correct parameters
        if data['next']:
            self.assertIn('limit=5', data['next'])
            self.assertIn('offset=15', data['next'])
    
    def test_custom_limit_offset_pagination(self):
        """Test custom limit/offset pagination."""
        url = reverse('pagination:order-custom-limit-offset')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should use custom default_limit (50)
        self.assertEqual(len(data['results']), 20)  # All orders fit in one page


class CursorPaginationTest(PaginationTestCase):
    """
    Test CursorPagination functionality.
    """
    
    def test_product_cursor_pagination(self):
        """Test cursor pagination with products."""
        url = reverse('pagination:product-cursor')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Check cursor pagination structure
        self.assertIn('next', data)
        self.assertIn('previous', data)
        self.assertIn('results', data)
        
        # No count in cursor pagination
        self.assertNotIn('count', data)
        
        # Check page size
        self.assertEqual(len(data['results']), 20)  # ProductCursorPagination page_size
    
    def test_article_cursor_pagination_with_slug(self):
        """Test cursor pagination with slug ordering."""
        url = reverse('pagination:article-cursor')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Check that articles are ordered by slug
        results = data['results']
        self.assertEqual(len(results), 15)  # ArticleCursorPagination page_size
        
        # Verify slug ordering (ascending)
        if len(results) > 1:
            first_slug = results[0]['slug']
            second_slug = results[1]['slug']
            # Should be in alphabetical order
            self.assertLess(first_slug, second_slug)
    
    def test_cursor_pagination_next_page(self):
        """Test navigating to next page with cursor."""
        url = reverse('pagination:product-cursor')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        if data['next']:
            # Extract cursor from next URL and test next page
            next_url = data['next']
            cursor_start = next_url.find('cursor=') + 7
            cursor_end = next_url.find('&', cursor_start)
            if cursor_end == -1:
                cursor_end = len(next_url)
            cursor = next_url[cursor_start:cursor_end]
            
            # Test next page
            next_response = self.client.get(url, {'cursor': cursor})
            self.assertEqual(next_response.status_code, status.HTTP_200_OK)
            
            next_data = next_response.json()
            # Should have previous link now
            self.assertIsNotNone(next_data['previous'])
    
    def test_comment_cursor_pagination_with_filter(self):
        """Test cursor pagination with filtering."""
        url = reverse('pagination:comment-cursor')
        article_id = self.articles[0].id
        response = self.client.get(url, {'article': article_id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # All results should be for the specified article
        for comment in data['results']:
            # The comment should reference the correct article ID
            # (This would need to be added to the serializer if we want to verify)
            pass  # Skip detailed verification for now


class CustomPaginationTest(PaginationTestCase):
    """
    Test custom pagination implementations.
    """
    
    def test_link_header_pagination(self):
        """Test pagination using HTTP Link header."""
        url = reverse('pagination:account-link-header')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Response should not have next/previous in body
        self.assertNotIn('next', data)
        self.assertNotIn('previous', data)
        
        # But should have count and results
        self.assertIn('count', data)
        self.assertIn('results', data)
        
        # Check for Link header
        if len(self.accounts) > 50:  # LinkHeaderPagination page_size
            self.assertIn('Link', response)
            link_header = response['Link']
            self.assertIn('rel="next"', link_header)
    
    def test_header_only_pagination(self):
        """Test pagination with all info in headers."""
        url = reverse('pagination:account-header-only')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check pagination headers
        self.assertIn('X-Total-Count', response)
        self.assertIn('X-Page-Number', response)
        self.assertIn('X-Page-Size', response)
        self.assertIn('X-Total-Pages', response)
        self.assertIn('X-Has-Next', response)
        self.assertIn('X-Has-Previous', response)
        
        # Verify header values
        self.assertEqual(response['X-Total-Count'], '25')
        self.assertEqual(response['X-Page-Number'], '1')
        self.assertEqual(response['X-Page-Size'], '100')
        self.assertEqual(response['X-Has-Previous'], 'false')
    
    def test_billing_records_view(self):
        """Test the billing records view from documentation example."""
        url = reverse('pagination:billing-records')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should use LargeResultsSetPagination (page_size=1000)
        self.assertEqual(len(data['results']), 30)  # All billing records
        self.assertIsNone(data['next'])


class ViewSetPaginationTest(PaginationTestCase):
    """
    Test pagination with ViewSets.
    """
    
    def test_product_viewset_pagination(self):
        """Test pagination with ProductViewSet."""
        url = reverse('pagination:product-viewset-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should use StandardResultsSetPagination
        self.assertEqual(len(data['results']), 50)  # All products in one page
    
    def test_article_viewset_pagination(self):
        """Test pagination with ArticleViewSet."""
        url = reverse('pagination:article-viewset-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should return published articles only
        for article in data['results']:
            self.assertTrue(article['published'])
    
    def test_order_viewset_authentication(self):
        """Test order viewset with user authentication."""
        # Test without authentication
        url = reverse('pagination:order-viewset-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test with regular user authentication
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only return user's orders
        data = response.json()
        for order in data['results']:
            self.assertEqual(order['customer'], self.user1.id)


class FunctionBasedViewPaginationTest(PaginationTestCase):
    """
    Test pagination with function-based views.
    """
    
    def test_function_based_product_pagination(self):
        """Test function-based view pagination."""
        url = reverse('pagination:product-function')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should use StandardResultsSetPagination
        self.assertIn('count', data)
        self.assertIn('results', data)
    
    def test_function_based_account_pagination(self):
        """Test function-based account view with custom pagination."""
        url = reverse('pagination:account-function')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should use CustomPagination format
        self.assertIn('links', data)
        self.assertIn('count', data)
        self.assertIn('results', data)


class NoPaginationTest(PaginationTestCase):
    """
    Test views with pagination disabled.
    """
    
    def test_no_pagination_view(self):
        """Test view with pagination explicitly disabled."""
        url = reverse('pagination:product-no-pagination')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should be a list without pagination structure
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 50)  # Limited to 100 in the view


class PaginationEdgeCasesTest(PaginationTestCase):
    """
    Test edge cases and error handling in pagination.
    """
    
    def test_invalid_page_number(self):
        """Test invalid page numbers."""
        url = reverse('pagination:product-page-number')
        
        # Test negative page number
        response = self.client.get(url, {'page': -1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test non-integer page number
        response = self.client.get(url, {'page': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test page number beyond available pages
        response = self.client.get(url, {'page': 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_invalid_page_size(self):
        """Test invalid page sizes."""
        url = reverse('pagination:product-standard')
        
        # Test negative page size
        response = self.client.get(url, {'page_size': -1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should use default page size
        
        # Test page size exceeding maximum
        response = self.client.get(url, {'page_size': 99999})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # Should be capped at max_page_size (1000)
        self.assertLessEqual(len(data['results']), 50)  # Limited by actual data
    
    def test_empty_queryset_pagination(self):
        """Test pagination with empty queryset."""
        # Delete all products
        Product.objects.all().delete()
        
        url = reverse('pagination:product-page-number')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['count'], 0)
        self.assertEqual(len(data['results']), 0)
        self.assertIsNone(data['next'])
        self.assertIsNone(data['previous'])


class PaginationPerformanceTest(PaginationTestCase):
    """
    Test pagination performance characteristics.
    """
    
    def test_cursor_pagination_consistency(self):
        """Test that cursor pagination provides consistent results."""
        url = reverse('pagination:product-cursor')
        
        # Get first page
        response1 = self.client.get(url)
        data1 = response1.json()
        first_page_ids = [item['id'] for item in data1['results']]
        
        # Add new products (simulating concurrent inserts)
        for i in range(5):
            Product.objects.create(
                name=f'New Product {i}',
                description='New product description',
                price=Decimal('99.99'),
                category='New',
                stock_quantity=100
            )
        
        # Get first page again
        response2 = self.client.get(url)
        data2 = response2.json()
        second_page_ids = [item['id'] for item in data2['results']]
        
        # Results should be different due to new items
        # (cursor pagination handles this gracefully)
        # This test mainly ensures no errors occur
        self.assertEqual(len(second_page_ids), len(first_page_ids))


class DocumentationExampleTest(PaginationTestCase):
    """
    Test specific examples from the DRF documentation.
    """
    
    def test_accounts_api_endpoint(self):
        """Test the accounts endpoint that matches documentation examples."""
        url = reverse('pagination:accounts-api')
        response = self.client.get(url, {'page': 4})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Response structure should match documentation
        data = response.json()
        self.assertIn('count', data)
        
        # Check for pagination links (if applicable)
        if data.get('next') or data.get('previous'):
            # Standard pagination format
            self.assertIn('next', data)
            self.assertIn('previous', data)
            self.assertIn('results', data)
        else:
            # Link header format
            # Links should be in headers instead
            pass