from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Purchase, Product, Category, UserProfile, Review, Booking
from .serializers import (
    PurchaseSerializer, ProductSerializer, CategorySerializer, 
    UserSerializer, ReviewSerializer, BookingSerializer
)


# =============================================================================
# BASIC FILTERING EXAMPLES FROM DOCUMENTATION
# =============================================================================

# Example 1: Filtering against the current user (from DRF documentation)
class PurchaseList(generics.ListAPIView):
    """
    This view should return a list of all the purchases
    for the currently authenticated user.
    (Example from DRF documentation)
    """
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return Purchase.objects.filter(purchaser=user)


# Example 2: Filtering against the URL (from DRF documentation)
class PurchaseListByUsername(generics.ListAPIView):
    """
    This view should return a list of all the purchases for
    the user as determined by the username portion of the URL.
    (Example from DRF documentation)
    """
    serializer_class = PurchaseSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        username = self.kwargs['username']
        return Purchase.objects.filter(purchaser__username=username)


# Example 3: Filtering against query parameters (from DRF documentation)
class PurchaseListWithQueryParams(generics.ListAPIView):
    """
    Optionally restricts the returned purchases to a given user,
    by filtering against a `username` query parameter in the URL.
    (Example from DRF documentation)
    """
    serializer_class = PurchaseSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Purchase.objects.all()
        username = self.request.query_params.get('username')
        if username is not None:
            queryset = queryset.filter(purchaser__username=username)
        return queryset


# =============================================================================
# EXTENDED BASIC FILTERING EXAMPLES
# =============================================================================

class ProductListWithBasicFiltering(generics.ListAPIView):
    """
    Product list with multiple query parameter filtering options.
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Filter products based on various query parameters.
        """
        queryset = Product.objects.all()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category is not None:
            queryset = queryset.filter(category__name__icontains=category)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price')
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by stock status
        in_stock = self.request.query_params.get('in_stock')
        if in_stock is not None:
            is_in_stock = in_stock.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(in_stock=is_in_stock)
        
        # Filter by owner (if authenticated)
        owner_only = self.request.query_params.get('owner_only')
        if owner_only and self.request.user.is_authenticated:
            if owner_only.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(owner=self.request.user)
        
        return queryset


class UserPurchasesByStatus(generics.ListAPIView):
    """
    View user's purchases filtered by status from URL.
    """
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return user's purchases filtered by status from URL parameter.
        """
        status = self.kwargs.get('status', 'all')
        queryset = Purchase.objects.filter(purchaser=self.request.user)
        
        if status != 'all':
            queryset = queryset.filter(status=status)
        
        return queryset


class ProductsByCategory(generics.ListAPIView):
    """
    Products filtered by category from URL.
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Return products filtered by category from URL.
        """
        category_name = self.kwargs['category_name']
        return Product.objects.filter(category__name__iexact=category_name)


class ReviewsByRating(generics.ListAPIView):
    """
    Reviews filtered by minimum rating from URL.
    """
    serializer_class = ReviewSerializer

    def get_queryset(self):
        """
        Return reviews with rating >= specified value.
        """
        min_rating = int(self.kwargs['min_rating'])
        return Review.objects.filter(rating__gte=min_rating)


# =============================================================================
# ADVANCED FILTERING WITH MULTIPLE PARAMETERS
# =============================================================================

class AdvancedProductFilter(generics.ListAPIView):
    """
    Advanced product filtering with multiple options.
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Advanced filtering with multiple parameters and date ranges.
        """
        queryset = Product.objects.all()
        
        # Text search in name and description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) | 
                models.Q(description__icontains=search)
            )
        
        # Category filtering
        categories = self.request.query_params.getlist('category')
        if categories:
            queryset = queryset.filter(category__name__in=categories)
        
        # Price range
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        # Stock filtering
        has_stock = self.request.query_params.get('has_stock')
        if has_stock is not None:
            if has_stock.lower() in ['true', '1']:
                queryset = queryset.filter(stock_quantity__gt=0)
            elif has_stock.lower() in ['false', '0']:
                queryset = queryset.filter(stock_quantity=0)
        
        # Date range filtering
        from django.utils.dateparse import parse_date
        created_after = self.request.query_params.get('created_after')
        created_before = self.request.query_params.get('created_before')
        
        if created_after:
            date_after = parse_date(created_after)
            if date_after:
                queryset = queryset.filter(created_at__date__gte=date_after)
        
        if created_before:
            date_before = parse_date(created_before)
            if date_before:
                queryset = queryset.filter(created_at__date__lte=date_before)
        
        # JSON field filtering (tags)
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__contains=[tag])
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset


class UserDashboardView(generics.ListAPIView):
    """
    User-specific dashboard with filtering.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return user-specific data based on view type.
        """
        view_type = self.request.query_params.get('type', 'products')
        user = self.request.user
        
        if view_type == 'products':
            return user.owned_products.all()
        elif view_type == 'purchases':
            return user.purchases.all()
        elif view_type == 'reviews':
            return user.reviews.all()
        else:
            return Product.objects.none()

    def get_serializer_class(self):
        """
        Return appropriate serializer based on view type.
        """
        view_type = self.request.query_params.get('type', 'products')
        
        if view_type == 'products':
            return ProductSerializer
        elif view_type == 'purchases':
            return PurchaseSerializer
        elif view_type == 'reviews':
            return ReviewSerializer
        else:
            return ProductSerializer


# =============================================================================
# EXAMPLES OF OVERRIDING INITIAL QUERYSET WITH GENERIC FILTERING
# =============================================================================

class PurchasedProductsList(generics.ListAPIView):
    """
    Return a list of all the products that the authenticated
    user has ever purchased, with optional filtering.
    (Example from DRF documentation)
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'in_stock']

    def get_queryset(self):
        """
        Return products purchased by the authenticated user.
        """
        user = self.request.user
        # Get products from user's purchases
        purchased_product_ids = user.purchases.values_list('product_id', flat=True)
        return Product.objects.filter(id__in=purchased_product_ids)


# =============================================================================
# VIEWSET EXAMPLES WITH FILTERING
# =============================================================================

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for products with comprehensive filtering.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'in_stock', 'owner']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'created_at', 'stock_quantity']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Optionally filter by user's own products.
        """
        queryset = Product.objects.all()
        
        # Filter by owner if requested
        my_products = self.request.query_params.get('my_products')
        if my_products and self.request.user.is_authenticated:
            if my_products.lower() in ['true', '1']:
                queryset = queryset.filter(owner=self.request.user)
        
        return queryset

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get products grouped by category.
        """
        category_name = request.query_params.get('category')
        if category_name:
            products = Product.objects.filter(category__name__icontains=category_name)
        else:
            products = Product.objects.all()
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """
        Get trending products (those with most reviews).
        """
        from django.db.models import Count
        
        products = Product.objects.annotate(
            review_count=Count('reviews')
        ).filter(
            review_count__gt=0
        ).order_by('-review_count')[:10]
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


# Import models for filtering
from django.db import models