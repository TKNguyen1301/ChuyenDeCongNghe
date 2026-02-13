from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views, filter_views, custom_filter_views

app_name = 'filtering'

# Router for ViewSets
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'custom-products', custom_filter_views.CustomFilteredProductViewSet, basename='custom-product')

urlpatterns = [
    # Include router URLs
    path('api/', include(router.urls)),
    
    # =============================================================================
    # BASIC FILTERING EXAMPLES (from documentation)
    # =============================================================================
    
    # Current user filtering
    path('purchases/', views.PurchaseList.as_view(), name='purchase-list'),
    
    # URL parameter filtering
    re_path(r'^purchases/(?P<username>.+)/$', views.PurchaseListByUsername.as_view(), name='purchase-by-username'),
    
    # Query parameter filtering
    path('purchases-query/', views.PurchaseListWithQueryParams.as_view(), name='purchase-query'),
    
    # Basic product filtering
    path('products-basic/', views.ProductListWithBasicFiltering.as_view(), name='products-basic'),
    
    # Status filtering from URL
    re_path(r'^user-purchases/(?P<status>\w+)/$', views.UserPurchasesByStatus.as_view(), name='user-purchases-status'),
    
    # Category filtering from URL
    re_path(r'^products/category/(?P<category_name>[\w\-]+)/$', views.ProductsByCategory.as_view(), name='products-by-category'),
    
    # Rating filtering from URL
    re_path(r'^reviews/rating/(?P<min_rating>[1-5])/$', views.ReviewsByRating.as_view(), name='reviews-by-rating'),
    
    # Advanced filtering
    path('products-advanced/', views.AdvancedProductFilter.as_view(), name='products-advanced'),
    path('user-dashboard/', views.UserDashboardView.as_view(), name='user-dashboard'),
    path('purchased-products/', views.PurchasedProductsList.as_view(), name='purchased-products'),
    
    # =============================================================================
    # DJANGO FILTER BACKEND EXAMPLES
    # =============================================================================
    
    # Simple DjangoFilterBackend
    path('products-simple-filter/', filter_views.ProductList.as_view(), name='products-simple-filter'),
    path('users-filter/', filter_views.UserListView.as_view(), name='users-filter'),
    
    # Advanced FilterSet examples
    path('products-advanced-filter/', filter_views.AdvancedProductListView.as_view(), name='products-advanced-filter'),
    path('purchases-advanced-filter/', filter_views.AdvancedPurchaseListView.as_view(), name='purchases-advanced-filter'),
    
    # =============================================================================
    # SEARCH FILTER EXAMPLES
    # =============================================================================
    
    # Basic search
    path('users-search/', filter_views.UserListWithSearch.as_view(), name='users-search'),
    path('products-search/', filter_views.ProductSearchView.as_view(), name='products-search'),
    path('products-advanced-search/', filter_views.AdvancedProductSearch.as_view(), name='products-advanced-search'),
    path('reviews-search/', filter_views.ReviewSearchView.as_view(), name='reviews-search'),
    
    # Custom search filter
    path('products-custom-search/', filter_views.CustomProductSearch.as_view(), name='products-custom-search'),
    
    # =============================================================================
    # ORDERING FILTER EXAMPLES
    # =============================================================================
    
    # Basic ordering
    path('users-ordering/', filter_views.UserListWithOrdering.as_view(), name='users-ordering'),
    path('products-ordering/', filter_views.ProductOrderingView.as_view(), name='products-ordering'),
    path('products-advanced-ordering/', filter_views.AdvancedProductOrdering.as_view(), name='products-advanced-ordering'),
    
    # Ordering with all fields
    path('bookings/', filter_views.BookingsListView.as_view(), name='bookings'),
    
    # Default ordering
    path('users-default-ordering/', filter_views.UserListWithDefaultOrdering.as_view(), name='users-default-ordering'),
    
    # =============================================================================
    # COMBINED FILTER EXAMPLES
    # =============================================================================
    
    # Comprehensive filtering
    path('products-comprehensive/', filter_views.ComprehensiveProductView.as_view(), name='products-comprehensive'),
    path('purchases-comprehensive/', filter_views.ComprehensivePurchaseView.as_view(), name='purchases-comprehensive'),
    path('user-purchases-filtered/', filter_views.UserPurchasesWithFiltering.as_view(), name='user-purchases-filtered'),
    
    # Filtered detail view
    path('products-filtered/<int:pk>/', filter_views.FilteredProductDetailView.as_view(), name='product-filtered-detail'),
    
    # =============================================================================
    # CUSTOM FILTER BACKEND EXAMPLES
    # =============================================================================
    
    # Owner-only filtering
    path('my-products/', custom_filter_views.MyProductsView.as_view(), name='my-products'),
    path('my-purchases/', custom_filter_views.MyPurchasesView.as_view(), name='my-purchases'),
    
    # Published only
    path('published-products/', custom_filter_views.PublishedProductsView.as_view(), name='published-products'),
    
    # Custom filter backends with HTML interface
    path('products-category-filter/', custom_filter_views.ProductsWithCategoryFilter.as_view(), name='products-category-filter'),
    path('products-price-filter/', custom_filter_views.ProductsWithPriceFilter.as_view(), name='products-price-filter'),
    path('products-date-filter/', custom_filter_views.ProductsWithDateFilter.as_view(), name='products-date-filter'),
    path('purchases-status-filter/', custom_filter_views.PurchasesWithStatusFilter.as_view(), name='purchases-status-filter'),
    path('products-advanced-search-custom/', custom_filter_views.ProductsWithAdvancedSearch.as_view(), name='products-advanced-search-custom'),
    
    # Combined custom filters
    path('products-combined-filters/', custom_filter_views.ProductsWithCombinedFilters.as_view(), name='products-combined-filters'),
    
    # Secure filtering (multiple custom filters)
    path('secure-products/', custom_filter_views.SecureProductsView.as_view(), name='secure-products'),
    path('comprehensive-products/', custom_filter_views.ComprehensiveProductFilter.as_view(), name='comprehensive-products'),
    path('my-secure-purchases/', custom_filter_views.MySecurePurchasesView.as_view(), name='my-secure-purchases'),
    path('bookings-filtered/', custom_filter_views.BookingWithMultipleFilters.as_view(), name='bookings-filtered'),
    
    # Demo view
    path('filter-demo/', custom_filter_views.FilterDemoView.as_view(), name='filter-demo'),
]