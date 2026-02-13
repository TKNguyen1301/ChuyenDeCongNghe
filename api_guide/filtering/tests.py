from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import Category, Product, Purchase, UserProfile, Review, Booking
from .serializers import ProductSerializer, PurchaseSerializer


class FilteringModelsTestCase(TestCase):
    """Test filtering models creation and relationships."""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.category = Category.objects.create(name='Electronics', description='Electronic products')
        
    def test_product_creation(self):
        """Test product creation with filtering fields."""
        product = Product.objects.create(
            name='Test Product',
            description='A test product',
            category=self.category,
            price=99.99,
            in_stock=True,
            stock_quantity=10,
            owner=self.user,
            tags=['test', 'demo']
        )
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.category, self.category)
        self.assertTrue(product.in_stock)
        self.assertEqual(product.tags, ['test', 'demo'])
    
    def test_purchase_creation(self):
        """Test purchase creation with relationships."""
        product = Product.objects.create(
            name='Test Product',
            description='A test product',
            category=self.category,
            price=99.99,
            owner=self.user
        )
        purchase = Purchase.objects.create(
            purchaser=self.user,
            product=product,
            quantity=2,
            total_price=199.98,
            status='completed'
        )
        self.assertEqual(purchase.purchaser, self.user)
        self.assertEqual(purchase.product, product)
        self.assertEqual(purchase.status, 'completed')


class BasicFilteringTestCase(APITestCase):
    """Test basic filtering examples from DRF documentation."""
    
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'password')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'password')
        self.category = Category.objects.create(name='Electronics')
        
        self.product1 = Product.objects.create(
            name='Product 1',
            description='First product',
            category=self.category,
            price=100.00,
            owner=self.user1
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            description='Second product',
            category=self.category,
            price=200.00,
            owner=self.user2
        )
        
        self.purchase1 = Purchase.objects.create(
            purchaser=self.user1,
            product=self.product1,
            quantity=1,
            total_price=100.00
        )
        self.purchase2 = Purchase.objects.create(
            purchaser=self.user2,
            product=self.product2,
            quantity=1,
            total_price=200.00
        )
    
    def test_current_user_filtering(self):
        """Test filtering purchases by current user."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('filtering:purchase-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['purchaser'], 'user1')
    
    def test_url_parameter_filtering(self):
        """Test filtering by username from URL parameter."""
        url = reverse('filtering:purchase-by-username', kwargs={'username': 'user1'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['purchaser'], 'user1')
    
    def test_query_parameter_filtering(self):
        """Test filtering by query parameters."""
        url = reverse('filtering:purchase-query')
        
        # Test with username parameter
        response = self.client.get(url, {'username': 'user1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test without username parameter (should return all)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_basic_product_filtering(self):
        """Test basic product filtering with multiple parameters."""
        url = reverse('filtering:products-basic')
        
        # Test category filtering
        response = self.client.get(url, {'category': 'Electronics'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Test price range filtering
        response = self.client.get(url, {'min_price': 150})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Product 2')
        
        response = self.client.get(url, {'max_price': 150})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Product 1')


class DjangoFilterBackendTestCase(APITestCase):
    """Test DjangoFilterBackend functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.category1 = Category.objects.create(name='Electronics')
        self.category2 = Category.objects.create(name='Books')
        
        self.product1 = Product.objects.create(
            name='Laptop',
            description='Gaming laptop',
            category=self.category1,
            price=1000.00,
            in_stock=True,
            owner=self.user
        )
        self.product2 = Product.objects.create(
            name='Book',
            description='Programming book',
            category=self.category2,
            price=50.00,
            in_stock=False,
            owner=self.user
        )
    
    def test_simple_django_filter(self):
        """Test simple DjangoFilterBackend with filterset_fields."""
        url = reverse('filtering:products-simple-filter')
        
        # Test category filtering
        response = self.client.get(url, {'category': self.category1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Laptop')
        
        # Test in_stock filtering
        response = self.client.get(url, {'in_stock': 'true'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Laptop')
        
        response = self.client.get(url, {'in_stock': 'false'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Book')
    
    def test_advanced_django_filter(self):
        """Test advanced DjangoFilterBackend with custom FilterSet."""
        url = reverse('filtering:products-advanced-filter')
        
        # Test name contains filtering
        response = self.client.get(url, {'name': 'Laptop'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test price range filtering
        response = self.client.get(url, {'price_min': 100, 'price_max': 500})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Book')
        
        # Test category name filtering
        response = self.client.get(url, {'category_name': 'Electronics'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Laptop')


class SearchFilterTestCase(APITestCase):
    """Test SearchFilter functionality."""
    
    def setUp(self):
        self.user1 = User.objects.create_user('john_doe', 'john@example.com', 'password')
        self.user2 = User.objects.create_user('jane_smith', 'jane@example.com', 'password')
        self.category = Category.objects.create(name='Electronics')
        
        self.product1 = Product.objects.create(
            name='MacBook Pro',
            description='Apple laptop computer',
            category=self.category,
            price=2000.00,
            owner=self.user1
        )
        self.product2 = Product.objects.create(
            name='Dell Laptop',
            description='Windows laptop computer',
            category=self.category,
            price=1000.00,
            owner=self.user2
        )
    
    def test_basic_search(self):
        """Test basic search functionality."""
        url = reverse('filtering:products-search')
        
        # Test search in name
        response = self.client.get(url, {'search': 'MacBook'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'MacBook Pro')
        
        # Test search in description
        response = self.client.get(url, {'search': 'Apple'})
        self.assertEqual(len(response.data['results']), 1)
        
        # Test search across multiple fields
        response = self.client.get(url, {'search': 'laptop'})
        self.assertEqual(len(response.data['results']), 2)
    
    def test_search_with_lookups(self):
        """Test search with different lookup types."""
        url = reverse('filtering:products-search')
        
        # Test exact match (=category__name)
        response = self.client.get(url, {'search': 'Electronics'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should find products in Electronics category
        
        # Test starts with (^name)
        response = self.client.get(url, {'search': 'Mac'})
        self.assertEqual(len(response.data['results']), 1)
    
    def test_user_search(self):
        """Test user search functionality."""
        url = reverse('filtering:users-search')
        
        # Test username search
        response = self.client.get(url, {'search': 'john'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test email search
        response = self.client.get(url, {'search': 'jane@example.com'})
        self.assertEqual(len(response.data['results']), 1)


class OrderingFilterTestCase(APITestCase):
    """Test OrderingFilter functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.category = Category.objects.create(name='Electronics')
        
        # Create products with different prices and names
        self.product1 = Product.objects.create(
            name='A Product',
            description='First product',
            category=self.category,
            price=300.00,
            owner=self.user
        )
        self.product2 = Product.objects.create(
            name='B Product',
            description='Second product',
            category=self.category,
            price=100.00,
            owner=self.user
        )
        self.product3 = Product.objects.create(
            name='C Product',
            description='Third product',
            category=self.category,
            price=200.00,
            owner=self.user
        )
    
    def test_ordering_by_name(self):
        """Test ordering by name."""
        url = reverse('filtering:products-ordering')
        
        # Test ascending order
        response = self.client.get(url, {'ordering': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item['name'] for item in response.data['results']]
        self.assertEqual(names, ['A Product', 'B Product', 'C Product'])
        
        # Test descending order
        response = self.client.get(url, {'ordering': '-name'})
        names = [item['name'] for item in response.data['results']]
        self.assertEqual(names, ['C Product', 'B Product', 'A Product'])
    
    def test_ordering_by_price(self):
        """Test ordering by price."""
        url = reverse('filtering:products-ordering')
        
        # Test ascending price order
        response = self.client.get(url, {'ordering': 'price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [float(item['price']) for item in response.data['results']]
        self.assertEqual(prices, [100.00, 200.00, 300.00])
        
        # Test descending price order
        response = self.client.get(url, {'ordering': '-price'})
        prices = [float(item['price']) for item in response.data['results']]
        self.assertEqual(prices, [300.00, 200.00, 100.00])
    
    def test_multiple_ordering(self):
        """Test ordering by multiple fields."""
        url = reverse('filtering:products-ordering')
        
        # Test ordering by category then name
        response = self.client.get(url, {'ordering': 'category,name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # All products are in same category, so should be ordered by name
        names = [item['name'] for item in response.data['results']]
        self.assertEqual(names, ['A Product', 'B Product', 'C Product'])
    
    def test_default_ordering(self):
        """Test default ordering behavior."""
        url = reverse('filtering:users-default-ordering')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be ordered by username by default


class CustomFilterBackendTestCase(APITestCase):
    """Test custom filter backends."""
    
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'password')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'password')
        self.category = Category.objects.create(name='Electronics')
        
        self.product1 = Product.objects.create(
            name='User1 Product',
            description='Product owned by user1',
            category=self.category,
            price=100.00,
            in_stock=True,
            owner=self.user1
        )
        self.product2 = Product.objects.create(
            name='User2 Product',
            description='Product owned by user2',
            category=self.category,
            price=200.00,
            in_stock=False,
            owner=self.user2
        )
    
    def test_owner_filter_backend(self):
        """Test IsOwnerFilterBackend."""
        url = reverse('filtering:my-products')
        
        # Test as user1
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'User1 Product')
        
        # Test as user2
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'User2 Product')
    
    def test_published_only_filter(self):
        """Test PublishedOnlyFilterBackend."""
        url = reverse('filtering:published-products')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'User1 Product')
    
    def test_category_filter_backend(self):
        """Test custom CategoryFilterBackend."""
        url = reverse('filtering:products-category-filter')
        
        # Test category filtering
        response = self.client.get(url, {'category': 'Electronics'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Test non-existent category
        response = self.client.get(url, {'category': 'Books'})
        self.assertEqual(len(response.data['results']), 0)
    
    def test_price_range_filter_backend(self):
        """Test custom PriceRangeFilterBackend."""
        url = reverse('filtering:products-price-filter')
        
        # Test minimum price
        response = self.client.get(url, {'min_price': '150'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'User2 Product')
        
        # Test maximum price
        response = self.client.get(url, {'max_price': '150'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'User1 Product')
        
        # Test price range
        response = self.client.get(url, {'min_price': '50', 'max_price': '150'})
        self.assertEqual(len(response.data['results']), 1)


class CombinedFilteringTestCase(APITestCase):
    """Test combination of multiple filters."""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.category1 = Category.objects.create(name='Electronics')
        self.category2 = Category.objects.create(name='Books')
        
        # Create multiple products for comprehensive testing
        self.product1 = Product.objects.create(
            name='MacBook Pro',
            description='Apple laptop computer',
            category=self.category1,
            price=2000.00,
            in_stock=True,
            stock_quantity=5,
            owner=self.user,
            tags=['apple', 'laptop']
        )
        self.product2 = Product.objects.create(
            name='Dell Laptop',
            description='Windows laptop computer',
            category=self.category1,
            price=1000.00,
            in_stock=True,
            stock_quantity=10,
            owner=self.user,
            tags=['dell', 'laptop']
        )
        self.product3 = Product.objects.create(
            name='Python Book',
            description='Learn Python programming',
            category=self.category2,
            price=50.00,
            in_stock=False,
            stock_quantity=0,
            owner=self.user,
            tags=['python', 'programming']
        )
    
    def test_comprehensive_filtering(self):
        """Test comprehensive product filtering combining all filter types."""
        url = reverse('filtering:products-comprehensive')
        
        # Test search + filtering + ordering
        response = self.client.get(url, {
            'search': 'laptop',
            'category': self.category1.id,
            'in_stock': 'true',
            'ordering': 'price'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Check ordering (Dell should come first due to lower price)
        self.assertEqual(response.data['results'][0]['name'], 'Dell Laptop')
        self.assertEqual(response.data['results'][1]['name'], 'MacBook Pro')
    
    def test_advanced_product_filtering(self):
        """Test advanced filtering with custom FilterSet."""
        url = reverse('filtering:products-advanced-filter')
        
        # Test name contains + price range
        response = self.client.get(url, {
            'name': 'Laptop',
            'price_min': 500,
            'price_max': 1500
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Dell Laptop')
        
        # Test JSON field filtering (tags)
        response = self.client.get(url, {'tag': 'apple'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'MacBook Pro')
    
    def test_filter_demo_view(self):
        """Test the filter demonstration view."""
        url = reverse('filtering:filter-demo')
        
        # Test basic demo
        response = self.client.get(url, {'demo_type': 'basic'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test published demo
        response = self.client.get(url, {'demo_type': 'published'})
        self.assertEqual(len(response.data['results']), 2)  # Only in-stock products
        
        # Test owned demo (requires authentication)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, {'demo_type': 'owned'})
        self.assertEqual(len(response.data['results']), 3)  # All user's products


class ViewSetFilteringTestCase(APITestCase):
    """Test filtering in ViewSets."""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.category = Category.objects.create(name='Electronics')
        
        self.product = Product.objects.create(
            name='Test Product',
            description='A test product',
            category=self.category,
            price=100.00,
            owner=self.user
        )
    
    def test_product_viewset_filtering(self):
        """Test filtering in ProductViewSet."""
        url = reverse('filtering:product-list')
        
        # Test search
        response = self.client.get(url, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test ordering
        response = self.client.get(url, {'ordering': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_custom_viewset_actions(self):
        """Test custom actions with filtering."""
        # Test my_products action
        self.client.force_authenticate(user=self.user)
        url = reverse('filtering:custom-product-my-products')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test filter_info action
        url = reverse('filtering:custom-product-filter-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('available_filters', response.data)
        self.assertIn('search_fields', response.data)