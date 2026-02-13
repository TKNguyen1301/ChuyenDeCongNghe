from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Product, Purchase, Review, Booking
from .serializers import ProductSerializer, PurchaseSerializer, ReviewSerializer, BookingSerializer
from .custom_filters import (
    IsOwnerFilterBackend, IsPurchaserFilterBackend, PublishedOnlyFilterBackend,
    CategoryFilterBackend, PriceRangeFilterBackend, DateRangeFilterBackend,
    StatusFilterBackend, AdvancedSearchFilterBackend, CombinedFilterBackend
)


# =============================================================================
# VIEWS USING CUSTOM FILTER BACKENDS
# =============================================================================

class MyProductsView(generics.ListAPIView):
    """
    View that only shows products owned by the current user.
    Uses IsOwnerFilterBackend from DRF documentation.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [IsOwnerFilterBackend]


class MyPurchasesView(generics.ListAPIView):
    """
    View that only shows purchases made by the current user.
    """
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [IsPurchaserFilterBackend]


class PublishedProductsView(generics.ListAPIView):
    """
    View that only shows products that are in stock.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [PublishedOnlyFilterBackend]


class ProductsWithCategoryFilter(generics.ListAPIView):
    """
    Products with custom category filter (includes HTML interface).
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [CategoryFilterBackend]


class ProductsWithPriceFilter(generics.ListAPIView):
    """
    Products with custom price range filter.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [PriceRangeFilterBackend]


class ProductsWithDateFilter(generics.ListAPIView):
    """
    Products with custom date range filter.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DateRangeFilterBackend]


class PurchasesWithStatusFilter(generics.ListAPIView):
    """
    Purchases with custom status filter.
    """
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    filter_backends = [StatusFilterBackend]


class ProductsWithAdvancedSearch(generics.ListAPIView):
    """
    Products with advanced search filter.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [AdvancedSearchFilterBackend]
    search_fields = ['name', 'description', '^category__name', '=owner__username']


class ProductsWithCombinedFilters(generics.ListAPIView):
    """
    Products with combined custom filters.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [CombinedFilterBackend]


# =============================================================================
# VIEWS COMBINING CUSTOM AND BUILT-IN FILTERS
# =============================================================================

class SecureProductsView(generics.ListAPIView):
    """
    Products that combines ownership check with other filters.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        IsOwnerFilterBackend,
        PublishedOnlyFilterBackend,
        CategoryFilterBackend,
        PriceRangeFilterBackend
    ]


class ComprehensiveProductFilter(generics.ListAPIView):
    """
    Products with comprehensive filtering combining custom and built-in filters.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        PublishedOnlyFilterBackend,  # Only in-stock products
        CategoryFilterBackend,       # Category filter with HTML
        PriceRangeFilterBackend,     # Price range filter
        AdvancedSearchFilterBackend, # Custom search
    ]
    search_fields = ['name', 'description', 'category__name']


class MySecurePurchasesView(generics.ListAPIView):
    """
    User's own purchases with additional filtering.
    """
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        IsPurchaserFilterBackend,  # Only user's purchases
        StatusFilterBackend,       # Filter by status
        DateRangeFilterBackend,    # Filter by date range
    ]


class BookingWithMultipleFilters(generics.ListAPIView):
    """
    Bookings with multiple custom filters.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [
        StatusFilterBackend,
        DateRangeFilterBackend,
    ]


# =============================================================================
# DEMONSTRATION VIEWS FOR FILTER COMBINATIONS
# =============================================================================

class FilterDemoView(generics.ListAPIView):
    """
    Demonstration view showing different filter combinations.
    Query parameters:
    - demo_type: 'basic', 'custom', 'combined', 'secure'
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        """Return different querysets based on demo type."""
        demo_type = self.request.query_params.get('demo_type', 'basic')
        
        if demo_type == 'basic':
            return Product.objects.all()
        elif demo_type == 'published':
            return Product.objects.filter(in_stock=True)
        elif demo_type == 'owned' and self.request.user.is_authenticated:
            return Product.objects.filter(owner=self.request.user)
        else:
            return Product.objects.all()

    def get_filter_backends(self):
        """Return different filter backends based on demo type."""
        demo_type = self.request.query_params.get('demo_type', 'basic')
        
        if demo_type == 'basic':
            return []
        elif demo_type == 'custom':
            return [CategoryFilterBackend, PriceRangeFilterBackend]
        elif demo_type == 'combined':
            return [CombinedFilterBackend]
        elif demo_type == 'secure':
            return [IsOwnerFilterBackend, PublishedOnlyFilterBackend]
        else:
            return []

    filter_backends = property(get_filter_backends)


# =============================================================================
# VIEWSET WITH CUSTOM FILTERS
# =============================================================================

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class CustomFilteredProductViewSet(viewsets.ModelViewSet):
    """
    Product ViewSet with custom filter backends.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        PublishedOnlyFilterBackend,
        CategoryFilterBackend,
        PriceRangeFilterBackend,
        AdvancedSearchFilterBackend
    ]
    search_fields = ['name', 'description', 'category__name']

    @action(detail=False, methods=['get'])
    def my_products(self, request):
        """Get current user's products."""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=401)
        
        queryset = Product.objects.filter(owner=request.user)
        
        # Apply the same filters as the main list
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(request, queryset, self)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def filter_info(self, request):
        """Get information about available filters."""
        filter_info = []
        
        for backend_class in self.filter_backends:
            backend = backend_class()
            info = {
                'name': backend.__class__.__name__,
                'description': getattr(backend, 'description', 'No description'),
            }
            
            # Add parameter information if available
            if hasattr(backend, 'category_param'):
                info['parameters'] = [backend.category_param]
            elif hasattr(backend, 'min_price_param'):
                info['parameters'] = [backend.min_price_param, backend.max_price_param]
            elif hasattr(backend, 'search_param'):
                info['parameters'] = [backend.search_param]
            
            filter_info.append(info)
        
        return Response({
            'available_filters': filter_info,
            'search_fields': getattr(self, 'search_fields', [])
        })