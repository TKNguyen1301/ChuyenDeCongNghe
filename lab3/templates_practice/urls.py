"""
URLs for Templates Practice App
"""
from django.urls import path
from . import views

app_name = 'templates_practice'

urlpatterns = [
    # Main views
    path('', views.HomeView.as_view(), name='home'),
    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('posts/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    
    # Category and Tag views
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('tags/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    
    # Template Examples
    path('examples/', views.TemplateExamplesListView.as_view(), name='examples_list'),
    path('examples/<int:pk>/', views.TemplateExampleDetailView.as_view(), name='example_detail'),
    path('examples/engine/', views.TemplateEngineView.as_view(), name='template_engine'),
    path('examples/filters/', views.TemplateFiltersView.as_view(), name='template_filters'),
    path('examples/tags/', views.TemplateTagsView.as_view(), name='template_tags'),
    path('examples/inheritance/', views.TemplateInheritanceView.as_view(), name='template_inheritance'),
    path('examples/custom-tags/', views.CustomTagsView.as_view(), name='custom_tags'),
    path('examples/context-processors/', views.ContextProcessorView.as_view(), name='context_processors'),
    path('examples/template-loading/', views.template_loader_examples, name='template_loading'),
    
    # Search
    path('search/', views.search_view, name='search'),
    
    # AJAX endpoints
    path('ajax/posts/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('ajax/newsletter/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('ajax/load-more-posts/', views.load_more_posts, name='load_more_posts'),
]
