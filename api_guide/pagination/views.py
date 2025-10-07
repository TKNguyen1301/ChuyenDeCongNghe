from rest_framework import generics, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import (
    PageNumberPagination, LimitOffsetPagination, CursorPagination
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    Product, Order, OrderItem, Article, Comment, 
    Billing, Account
)
from .serializers import (
    ProductSerializer, OrderSerializer, OrderItemSerializer,
    ArticleSerializer, ArticleDetailSerializer, CommentSerializer,
    BillingSerializer, AccountSerializer,
    MinimalProductSerializer, MinimalAccountSerializer
)
from .pagination import (
    LargeResultsSetPagination, StandardResultsSetPagination,
    CustomPagination, LinkHeaderPagination,
    CustomLimitOffsetPagination, CustomCursorPagination,
    ProductCursorPagination, ArticleCursorPagination,
    FlexiblePagination, HeaderPagination
)


# ============================================================================
# PageNumberPagination Examples
# ============================================================================

class ProductListView(generics.ListCreateAPIView):
    """
    Basic product list using default PageNumberPagination (if configured globally).
    Demonstrates the most basic pagination setup.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created']


class ProductPageNumberView(generics.ListAPIView):
    """
    Product list using explicit PageNumberPagination.
    Shows the basic page number pagination style.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination


class ProductCustomPaginationView(generics.ListAPIView):
    """
    Product list using CustomPagination with nested links.
    Demonstrates the custom response format from the documentation.
    """
    queryset = Product.objects.all()
    serializer_class = MinimalProductSerializer
    pagination_class = CustomPagination


class ProductLargePaginationView(generics.ListAPIView):
    """
    Product list using LargeResultsSetPagination.
    For handling large datasets with customizable page sizes.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = LargeResultsSetPagination


class ProductStandardPaginationView(generics.ListAPIView):
    """
    Product list using StandardResultsSetPagination.
    Standard configuration for most use cases.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination


class ProductFlexiblePaginationView(generics.ListAPIView):
    """
    Product list using FlexiblePagination.
    Supports dynamic page sizes including 'max' parameter.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = FlexiblePagination


# ============================================================================
# LimitOffsetPagination Examples
# ============================================================================

class OrderLimitOffsetView(generics.ListAPIView):
    """
    Order list using default LimitOffsetPagination.
    Demonstrates limit/offset style pagination.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = LimitOffsetPagination


class OrderCustomLimitOffsetView(generics.ListAPIView):
    """
    Order list using CustomLimitOffsetPagination.
    Shows customized limit/offset pagination parameters.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = CustomLimitOffsetPagination


class OrderItemLimitOffsetView(generics.ListAPIView):
    """
    Order items using limit/offset pagination with filtering.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['order', 'product']


# ============================================================================
# CursorPagination Examples
# ============================================================================

class ProductCursorView(generics.ListAPIView):
    """
    Product list using CursorPagination.
    Demonstrates cursor-based pagination for consistent results.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductCursorPagination


class ArticleCursorView(generics.ListAPIView):
    """
    Article list using CursorPagination with slug ordering.
    Shows cursor pagination with unique field ordering.
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    pagination_class = ArticleCursorPagination


class ArticleCustomCursorView(generics.ListAPIView):
    """
    Article list using CustomCursorPagination.
    Demonstrates custom cursor pagination configuration.
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    pagination_class = CustomCursorPagination


class CommentCursorView(generics.ListAPIView):
    """
    Comment list using CursorPagination with ascending order.
    Shows cursor pagination with different ordering.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CursorPagination

    def get_queryset(self):
        """Filter comments by article if specified."""
        queryset = Comment.objects.all()
        article_id = self.request.query_params.get('article', None)
        if article_id is not None:
            queryset = queryset.filter(article=article_id)
        return queryset


# ============================================================================
# Custom Pagination Examples
# ============================================================================

class AccountLinkHeaderView(generics.ListAPIView):
    """
    Account list using LinkHeaderPagination.
    Demonstrates HTTP Link header pagination.
    """
    queryset = Account.objects.all()
    serializer_class = MinimalAccountSerializer
    pagination_class = LinkHeaderPagination


class BillingRecordsView(generics.ListAPIView):
    """
    Billing records view from the documentation example.
    Uses LargeResultsSetPagination as shown in the docs.
    """
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer
    pagination_class = LargeResultsSetPagination


class AccountHeaderPaginationView(generics.ListAPIView):
    """
    Account list using HeaderPagination.
    All pagination info is in response headers.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    pagination_class = HeaderPagination


# ============================================================================
# ViewSet Examples
# ============================================================================

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Product ViewSet demonstrating pagination with ViewSets.
    Uses StandardResultsSetPagination.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created']


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Article ViewSet with different serializers for list/detail actions.
    """
    queryset = Article.objects.filter(published=True)
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['author']
    search_fields = ['title', 'content']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleSerializer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Order ViewSet using cursor pagination for consistent ordering.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = CustomCursorPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'customer']

    def get_queryset(self):
        """Filter orders by current user if authenticated."""
        queryset = Order.objects.all()
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            queryset = queryset.filter(customer=user)
        return queryset


# ============================================================================
# Function-Based View Examples
# ============================================================================

@api_view(['GET'])
def product_list_function_view(request):
    """
    Function-based view demonstrating manual pagination implementation.
    Shows how to use pagination API with regular APIView.
    """
    products = Product.objects.all()
    
    # Apply filtering if needed
    category = request.query_params.get('category', None)
    if category is not None:
        products = products.filter(category=category)
    
    # Initialize paginator
    paginator = StandardResultsSetPagination()
    
    # Paginate the queryset
    page = paginator.paginate_queryset(products, request)
    if page is not None:
        serializer = ProductSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    # If pagination is not enabled
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def account_list_function_view(request):
    """
    Function-based view using CustomPagination.
    Matches the documentation examples for accounts API.
    """
    accounts = Account.objects.all()
    
    # Initialize custom paginator
    paginator = CustomPagination()
    
    # Paginate the queryset
    page = paginator.paginate_queryset(accounts, request)
    if page is not None:
        serializer = AccountSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = AccountSerializer(accounts, many=True)
    return Response(serializer.data)


# ============================================================================
# Special Use Case Views
# ============================================================================

class HighVolumeProductView(generics.ListAPIView):
    """
    View optimized for high-volume product listings.
    Uses cursor pagination for performance with large datasets.
    """
    queryset = Product.objects.all()
    serializer_class = MinimalProductSerializer
    pagination_class = ProductCursorPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']


class PublicArticleView(generics.ListAPIView):
    """
    Public article view with different pagination for public access.
    """
    queryset = Article.objects.filter(published=True)
    serializer_class = ArticleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created', 'view_count']


class UserOrderHistoryView(generics.ListAPIView):
    """
    User-specific order history with cursor pagination.
    """
    serializer_class = OrderSerializer
    pagination_class = CustomCursorPagination

    def get_queryset(self):
        """Return orders for the current user only."""
        return Order.objects.filter(customer=self.request.user)


# ============================================================================
# No Pagination Examples
# ============================================================================

class NoPaginationView(generics.ListAPIView):
    """
    View with pagination explicitly disabled.
    Returns all results in a single response.
    """
    queryset = Product.objects.all()[:100]  # Limit to prevent huge responses
    serializer_class = MinimalProductSerializer
    pagination_class = None