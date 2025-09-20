"""
URLconf for Class-based Views Practice
Demonstrates URL patterns with class-based views using .as_view()
"""

from django.urls import path
from . import views

app_name = 'cbv_practice'

urlpatterns = [
    # =============================================================================
    # HOME AND BASIC VIEWS
    # =============================================================================
    
    # Homepage
    path('', views.HomeView.as_view(), name='home'),
    
    # About page using TemplateView
    path('about/', views.AboutView.as_view(), name='about'),
    
    # Basic View class example
    path('basic/', views.BasicView.as_view(), name='basic-view'),
    
    # JSON response view
    path('api/info/', views.JSONResponseView.as_view(), name='json-response'),
    
    # Statistics dashboard
    path('stats/', views.StatsView.as_view(), name='stats'),
    
    # =============================================================================
    # REDIRECT VIEWS
    # =============================================================================
    
    # Redirect examples
    path('old-books/', views.OldBooksRedirectView.as_view(), name='old-books-redirect'),
    path('random-book/', views.RandomBookRedirectView.as_view(), name='random-book'),
    
    # =============================================================================
    # BOOK VIEWS (ListView and DetailView examples)
    # =============================================================================
    
    # Book list with filtering and pagination
    path('books/', views.BookListView.as_view(), name='book-list'),
    
    # Enhanced book list with mixins
    path('books/enhanced/', views.EnhancedBookListView.as_view(), name='enhanced-book-list'),
    
    # Book detail view
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    
    # =============================================================================
    # AUTHOR VIEWS
    # =============================================================================
    
    # Author list
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    
    # Author detail view
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    
    # =============================================================================
    # ARTICLE VIEWS
    # =============================================================================
    
    # Article list with category filtering
    path('articles/', views.ArticleListView.as_view(), name='article-list'),
    
    # Article detail view (using slug)
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article-detail'),
    
    # Add comment to article (FormView example)
    path('articles/<slug:slug>/comment/', views.ArticleCommentView.as_view(), name='add-comment'),
    
    # =============================================================================
    # CATEGORY VIEWS
    # =============================================================================
    
    # Category detail view
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # =============================================================================
    # ASYNCHRONOUS VIEWS
    # =============================================================================
    
    # Simple async view
    path('async/', views.AsyncView.as_view(), name='async-view'),
    
    # Complex async view with multiple operations
    path('async/stats/', views.AsyncBookStatsView.as_view(), name='async-stats'),
]
