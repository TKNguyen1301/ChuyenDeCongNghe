from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, function_views

app_name = 'caching'

# Router for ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'cached-posts', views.CachedPostViewSet, basename='cached-post')

urlpatterns = [
    # Include router URLs
    path('api/', include(router.urls)),
    
    # Class-based views from documentation examples
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('post/', views.PostView.as_view(), name='post'),
    path('cached-post-list/', views.CachedPostListView.as_view(), name='cached-post-list'),
    path('user-specific/', views.UserSpecificCachedView.as_view(), name='user-specific'),
    path('conditional-cache/', views.ConditionalCacheView.as_view(), name='conditional-cache'),
    path('cache-invalidation/', views.CacheInvalidationView.as_view(), name='cache-invalidation'),
    path('cache-stats/', views.CacheStatsView.as_view(), name='cache-stats'),
    
    # Function-based views from documentation examples
    path('function/user-list/', function_views.get_user_list, name='function-user-list'),
    path('function/public-posts/', function_views.get_public_posts, name='function-public-posts'),
    path('function/user-dashboard/', function_views.get_user_dashboard, name='function-user-dashboard'),
    path('function/user-stats/', function_views.get_user_stats, name='function-user-stats'),
    path('function/post/<int:post_id>/', function_views.get_cached_post_by_id, name='function-post-detail'),
    path('function/author/<str:username>/', function_views.get_posts_by_author, name='function-posts-by-author'),
    path('function/site-stats/', function_views.get_site_statistics, name='function-site-stats'),
    path('function/invalidate-user-cache/', function_views.invalidate_user_cache, name='function-invalidate-user-cache'),
    path('function/test-performance/', function_views.test_cache_performance, name='function-test-performance'),
]