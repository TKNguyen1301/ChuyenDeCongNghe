import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

from .models import Product, Purchase, Category, Review, Booking, UserProfile
from .serializers import (
    ProductSerializer, PurchaseSerializer, CategorySerializer, 
    ReviewSerializer, BookingSerializer, UserSerializer
)


# =============================================================================
# DJANGO FILTER BACKEND EXAMPLES
# =============================================================================

# Example from DRF documentation: Simple filterset_fields
class ProductList(generics.ListAPIView):
    """
    Product list with simple DjangoFilterBackend filtering.
    Example from DRF documentation.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'in_stock']


class UserListView(generics.ListAPIView):
    """
    User list with DjangoFilterBackend.
    Example from DRF documentation.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]


# =============================================================================
# ADVANCED DJANGO FILTER EXAMPLES WITH CUSTOM FILTERSETS
# =============================================================================

class ProductFilter(django_filters.FilterSet):
    """
    Custom FilterSet for advanced product filtering.
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    owner_username = django_filters.CharFilter(field_name='owner__username', lookup_expr='iexact')
    has_stock = django_filters.BooleanFilter(field_name='stock_quantity', lookup_expr='gt', label='Has Stock')
    
    # Range filters
    price = django_filters.RangeFilter()
    stock_quantity = django_filters.RangeFilter()
    
    # Choice filter
    in_stock = django_filters.BooleanFilter()
    
    # Multiple choice filter for tags (JSON field)
    tag = django_filters.CharFilter(method='filter_by_tag')
    
    def filter_by_tag(self, queryset, name, value):
        """Custom method to filter by tags in JSON field."""
        return queryset.filter(tags__contains=[value])

    class Meta:
        model = Product
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'price': ['exact', 'gte', 'lte', 'gt', 'lt'],
            'category': ['exact'],
            'in_stock': ['exact'],
            'created_at': ['exact', 'gte', 'lte', 'year', 'month', 'day'],
        }


class AdvancedProductListView(generics.ListAPIView):
    """
    Product list using custom FilterSet.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class PurchaseFilter(django_filters.FilterSet):
    """
    Custom FilterSet for purchase filtering.
    """
    purchaser_username = django_filters.CharFilter(field_name='purchaser__username', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='product__name', lookup_expr='icontains')
    product_category = django_filters.CharFilter(field_name='product__category__name', lookup_expr='iexact')
    total_price_min = django_filters.NumberFilter(field_name='total_price', lookup_expr='gte')
    total_price_max = django_filters.NumberFilter(field_name='total_price', lookup_expr='lte')
    purchase_date_after = django_filters.DateFilter(field_name='purchase_date', lookup_expr='date__gte')
    purchase_date_before = django_filters.DateFilter(field_name='purchase_date', lookup_expr='date__lte')
    
    # Date range filter
    purchase_date = django_filters.DateFromToRangeFilter()
    total_price = django_filters.RangeFilter()
    
    # Multiple choice
    status = django_filters.MultipleChoiceFilter(
        choices=Purchase._meta.get_field('status').choices
    )

    class Meta:
        model = Purchase
        fields = ['status', 'quantity']


class AdvancedPurchaseListView(generics.ListAPIView):
    """
    Purchase list with advanced filtering.
    """
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PurchaseFilter


# =============================================================================
# SEARCH FILTER EXAMPLES
# =============================================================================

class UserListWithSearch(generics.ListAPIView):
    """
    User list with SearchFilter.
    Example from DRF documentation.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']


class ProductSearchView(generics.ListAPIView):
    """
    Product search with various search field types.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'name',                     # Default: icontains
        'description',              # Default: icontains
        '=category__name',          # Exact match
        '^name',                    # Starts with
        '$description',             # Regex search
        'owner__username',          # Related field search
        'owner__email',             # Related field search
    ]


class AdvancedProductSearch(generics.ListAPIView):
    """
    Advanced product search with related field lookups.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'name',
        'description', 
        'category__name',
        'owner__username',
        'owner__first_name',
        'owner__last_name',
        'owner__filtering_profile__profession',  # Deep relationship
    ]


class ReviewSearchView(generics.ListAPIView):
    """
    Review search with multiple field types.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'title',
        'content',
        '=reviewer__username',      # Exact match for username
        '^product__name',           # Starts with for product name
        'product__description',
    ]


# Custom SearchFilter example
class CustomSearchFilter(filters.SearchFilter):
    """
    Custom SearchFilter that changes search fields based on request.
    Example from DRF documentation.
    """
    def get_search_fields(self, view, request):
        """
        Override to dynamically change search fields.
        """
        if request.query_params.get('title_only'):
            return ['title']
        return super().get_search_fields(view, request)


class CustomProductSearch(generics.ListAPIView):
    """
    Product search using custom SearchFilter.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [CustomSearchFilter]
    search_fields = ['name', 'description', 'category__name']


# =============================================================================
# ORDERING FILTER EXAMPLES
# =============================================================================

class UserListWithOrdering(generics.ListAPIView):
    """
    User list with OrderingFilter.
    Example from DRF documentation.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['username', 'email']


class ProductOrderingView(generics.ListAPIView):
    """
    Product list with comprehensive ordering options.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name', 'price', 'created_at', 'stock_quantity']
    ordering = ['name']  # Default ordering


class AdvancedProductOrdering(generics.ListAPIView):
    """
    Product ordering with related field ordering.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = [
        'name', 'price', 'created_at', 'stock_quantity',
        'category__name', 'owner__username'
    ]
    ordering = ['-created_at']


class BookingsListView(generics.ListAPIView):
    """
    Booking list allowing ordering on any field.
    Example from DRF documentation.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = '__all__'


class UserListWithDefaultOrdering(generics.ListAPIView):
    """
    User list with default ordering.
    Example from DRF documentation.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['username', 'email']
    ordering = ['username']


# =============================================================================
# COMBINED FILTER EXAMPLES
# =============================================================================

class ComprehensiveProductView(generics.ListAPIView):
    """
    Product view combining all filter types.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name', 'owner__username']
    ordering_fields = ['name', 'price', 'created_at', 'stock_quantity']
    ordering = ['-created_at']


class ComprehensivePurchaseView(generics.ListAPIView):
    """
    Purchase view with all filter types.
    """
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PurchaseFilter
    search_fields = [
        'product__name', 'purchaser__username', 'notes',
        'product__category__name'
    ]
    ordering_fields = [
        'purchase_date', 'total_price', 'quantity',
        'purchaser__username', 'product__name'
    ]
    ordering = ['-purchase_date']


class UserPurchasesWithFiltering(generics.ListAPIView):
    """
    User's purchases with comprehensive filtering.
    """
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PurchaseFilter
    search_fields = ['product__name', 'notes']
    ordering_fields = ['purchase_date', 'total_price', 'quantity']
    ordering = ['-purchase_date']

    def get_queryset(self):
        """
        Return only the current user's purchases.
        """
        return Purchase.objects.filter(purchaser=self.request.user)


# =============================================================================
# FILTERING WITH OBJECT LOOKUPS EXAMPLE
# =============================================================================

class FilteredProductDetailView(generics.RetrieveAPIView):
    """
    Product detail view that respects filtering.
    Example showing how filters apply to single object lookups.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'in_stock']
    
    # This will return 404 if the product doesn't match filter conditions
    # Example: /api/products/4675/?category=clothing&in_stock=true