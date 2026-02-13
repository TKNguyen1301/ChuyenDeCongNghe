from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'products-viewset', views.ProductViewSet)
router.register(r'articles-viewset', views.ArticleViewSet)
router.register(r'orders-viewset', views.OrderViewSet)

app_name = 'pagination'

urlpatterns = [
    # ========================================================================
    # PageNumberPagination Examples
    # ========================================================================
    
    # Basic product list (uses global pagination if configured)
    path('products/', views.ProductListView.as_view(), name='product-list'),
    
    # Explicit PageNumberPagination
    path('products/page-number/', views.ProductPageNumberView.as_view(), 
         name='product-page-number'),
    
    # Custom pagination with nested links
    path('products/custom/', views.ProductCustomPaginationView.as_view(), 
         name='product-custom'),
    
    # Large results pagination
    path('products/large/', views.ProductLargePaginationView.as_view(), 
         name='product-large'),
    
    # Standard results pagination
    path('products/standard/', views.ProductStandardPaginationView.as_view(), 
         name='product-standard'),
    
    # Flexible pagination (supports page_size=max)
    path('products/flexible/', views.ProductFlexiblePaginationView.as_view(), 
         name='product-flexible'),
    
    # ========================================================================
    # LimitOffsetPagination Examples
    # ========================================================================
    
    # Basic limit/offset pagination
    path('orders/limit-offset/', views.OrderLimitOffsetView.as_view(), 
         name='order-limit-offset'),
    
    # Custom limit/offset pagination
    path('orders/custom-limit-offset/', views.OrderCustomLimitOffsetView.as_view(), 
         name='order-custom-limit-offset'),
    
    # Order items with limit/offset
    path('order-items/limit-offset/', views.OrderItemLimitOffsetView.as_view(), 
         name='order-item-limit-offset'),
    
    # ========================================================================
    # CursorPagination Examples
    # ========================================================================
    
    # Product cursor pagination
    path('products/cursor/', views.ProductCursorView.as_view(), 
         name='product-cursor'),
    
    # Article cursor pagination with slug ordering
    path('articles/cursor/', views.ArticleCursorView.as_view(), 
         name='article-cursor'),
    
    # Article custom cursor pagination
    path('articles/custom-cursor/', views.ArticleCustomCursorView.as_view(), 
         name='article-custom-cursor'),
    
    # Comment cursor pagination
    path('comments/cursor/', views.CommentCursorView.as_view(), 
         name='comment-cursor'),
    
    # ========================================================================
    # Custom Pagination Examples
    # ========================================================================
    
    # Account list with Link header pagination
    path('accounts/link-header/', views.AccountLinkHeaderView.as_view(), 
         name='account-link-header'),
    
    # Billing records (documentation example)
    path('billing/', views.BillingRecordsView.as_view(), 
         name='billing-records'),
    
    # Account list with header-only pagination
    path('accounts/header-only/', views.AccountHeaderPaginationView.as_view(), 
         name='account-header-only'),
    
    # ========================================================================
    # Function-Based View Examples
    # ========================================================================
    
    # Function-based product list
    path('products/function/', views.product_list_function_view, 
         name='product-function'),
    
    # Function-based account list (documentation example)
    path('accounts/function/', views.account_list_function_view, 
         name='account-function'),
    
    # ========================================================================
    # Special Use Cases
    # ========================================================================
    
    # High-volume product listing
    path('products/high-volume/', views.HighVolumeProductView.as_view(), 
         name='product-high-volume'),
    
    # Public article view
    path('articles/public/', views.PublicArticleView.as_view(), 
         name='article-public'),
    
    # User order history
    path('orders/my-history/', views.UserOrderHistoryView.as_view(), 
         name='order-history'),
    
    # No pagination example
    path('products/no-pagination/', views.NoPaginationView.as_view(), 
         name='product-no-pagination'),
    
    # ========================================================================
    # ViewSet URLs (via router)
    # ========================================================================
    path('', include(router.urls)),
    
    # ========================================================================
    # Documentation Example URLs (matching the docs)
    # ========================================================================
    
    # These match the URLs shown in the DRF documentation examples
    path('accounts/', views.AccountLinkHeaderView.as_view(), 
         name='accounts-api'),  # Matches https://api.example.org/accounts/
]