"""
Class-based Views Practice - Django Documentation Implementation
https://docs.djangoproject.com/en/5.2/topics/class-based-views/

This module demonstrates various types of Class-based Views:
1. Basic View class
2. TemplateView 
3. RedirectView
4. ListView
5. DetailView
6. CreateView, UpdateView, DeleteView
7. Custom mixins and advanced patterns
8. Asynchronous class-based views
"""

import asyncio
from datetime import timedelta
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views import View
from django.views.generic import (
    TemplateView, RedirectView, ListView, DetailView, 
    CreateView, UpdateView, DeleteView, FormView
)
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django import forms

from .models import Book, Author, Article, Category, Comment


# =============================================================================
# 1. BASIC VIEW CLASS EXAMPLES
# =============================================================================

class BasicView(View):
    """
    Simplest form of class-based view using Django's base View class.
    Demonstrates HTTP method dispatch.
    """
    
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h1>Basic Class-based View</h1>'
                          '<p>This is a GET request response</p>'
                          '<form method="post">'
                          '<input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">'
                          '<button type="submit">Send POST</button>'
                          '</form>')
    
    def post(self, request, *args, **kwargs):
        return HttpResponse('<h1>POST Request Received</h1>'
                          '<p>Data received via POST method</p>'
                          '<a href="?">Back to GET</a>')


class JSONResponseView(View):
    """
    View that returns JSON responses - useful for APIs
    """
    
    def get(self, request, *args, **kwargs):
        data = {
            'message': 'Hello from Class-based View',
            'method': 'GET',
            'timestamp': timezone.now().isoformat(),
            'user': str(request.user) if request.user.is_authenticated else 'Anonymous'
        }
        return JsonResponse(data)


# =============================================================================
# 2. TEMPLATEVIEW EXAMPLES  
# =============================================================================

class AboutView(TemplateView):
    """
    Basic TemplateView example - renders a template with context
    """
    template_name = "cbv_practice/about.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'About Our Library',
            'description': 'Welcome to our digital library system',
            'features': [
                'Browse books by category',
                'Read articles from various authors', 
                'Search functionality',
                'User-friendly interface'
            ],
            'stats': {
                'total_books': Book.objects.count(),
                'total_authors': Author.objects.count(),
                'total_articles': Article.objects.filter(is_published=True).count(),
                'total_categories': Category.objects.count(),
            }
        })
        return context


class HomeView(TemplateView):
    """
    Homepage with dynamic content
    """
    template_name = "cbv_practice/home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'recent_books': Book.objects.filter(is_available=True)[:5],
            'featured_articles': Article.objects.filter(is_published=True)[:3],
            'popular_categories': Category.objects.annotate(
                book_count=Count('books')
            ).order_by('-book_count')[:5],
            'new_releases': Book.objects.filter(
                publication_date__gte=timezone.now().date() - timedelta(days=30)
            )[:3]
        })
        return context


# =============================================================================
# 3. REDIRECTVIEW EXAMPLES
# =============================================================================

class OldBooksRedirectView(RedirectView):
    """
    Permanent redirect from old URL pattern to new one
    """
    permanent = True
    pattern_name = 'cbv_practice:book-list'


class RandomBookRedirectView(RedirectView):
    """
    Redirect to a random book detail page
    """
    permanent = False
    
    def get_redirect_url(self, *args, **kwargs):
        book = Book.objects.filter(is_available=True).order_by('?').first()
        if book:
            return reverse('cbv_practice:book-detail', kwargs={'pk': book.pk})
        return reverse('cbv_practice:book-list')


# =============================================================================
# 4. LISTVIEW EXAMPLES
# =============================================================================

class BookListView(ListView):
    """
    Complete ListView example with pagination, filtering, and context
    Demonstrates HEAD method support as mentioned in Django docs
    """
    model = Book
    template_name = 'cbv_practice/book_list.html'
    context_object_name = 'books'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Book.objects.select_related('category').prefetch_related('authors')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(authors__name__icontains=search)
            ).distinct()
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
            
        # Availability filter
        available_only = self.request.GET.get('available_only')
        if available_only:
            queryset = queryset.filter(is_available=True)
            
        return queryset.order_by('-publication_date', 'title')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': Category.objects.all(),
            'search_query': self.request.GET.get('search', ''),
            'selected_category': self.request.GET.get('category', ''),
            'total_count': self.get_queryset().count(),
        })
        return context
    
    def head(self, *args, **kwargs):
        """
        Supporting HEAD method as shown in Django documentation
        Returns Last-Modified header based on most recent book
        """
        last_book = self.get_queryset().first()
        response = HttpResponse()
        if last_book:
            response['Last-Modified'] = last_book.updated_at.strftime(
                "%a, %d %b %Y %H:%M:%S GMT"
            )
        return response


class AuthorListView(ListView):
    """
    Author listing with custom ordering and context
    """
    model = Author
    template_name = 'cbv_practice/author_list.html'
    context_object_name = 'authors'
    paginate_by = 15
    
    def get_queryset(self):
        return Author.objects.annotate(
            book_count=Count('books'),
            article_count=Count('articles')
        ).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_authors'] = Author.objects.count()
        return context


class ArticleListView(ListView):
    """
    Published articles with category filtering
    """
    model = Article
    template_name = 'cbv_practice/article_list.html'
    context_object_name = 'articles'
    paginate_by = 8
    
    def get_queryset(self):
        queryset = Article.objects.filter(is_published=True).select_related(
            'author', 'category'
        )
        
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            
        return queryset.order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': Category.objects.annotate(
                article_count=Count('articles', filter=Q(articles__is_published=True))
            ).filter(article_count__gt=0),
            'selected_category': self.request.GET.get('category', ''),
        })
        return context


# =============================================================================
# 5. DETAILVIEW EXAMPLES
# =============================================================================

class BookDetailView(DetailView):
    """
    Book detail with related objects and view counting
    """
    model = Book
    template_name = 'cbv_practice/book_detail.html'
    context_object_name = 'book'
    
    def get_queryset(self):
        return Book.objects.select_related('category').prefetch_related('authors')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object
        context.update({
            'related_books': Book.objects.filter(
                category=book.category
            ).exclude(pk=book.pk)[:4],
            'author_articles': Article.objects.filter(
                author__in=book.authors.all(),
                is_published=True
            )[:3]
        })
        return context


class AuthorDetailView(DetailView):
    """
    Author detail with their books and articles
    """
    model = Author
    template_name = 'cbv_practice/author_detail.html'
    context_object_name = 'author'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.object
        context.update({
            'books': author.books.filter(is_available=True)[:10],
            'articles': author.articles.filter(is_published=True)[:5],
            'total_books': author.books.count(),
            'total_articles': author.articles.filter(is_published=True).count(),
        })
        return context


class ArticleDetailView(DetailView):
    """
    Article detail with comments and view counting
    """
    model = Article
    template_name = 'cbv_practice/article_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    
    def get_queryset(self):
        return Article.objects.filter(is_published=True).select_related('author', 'category')
    
    def get_object(self):
        """Override to increment view count"""
        obj = super().get_object()
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        context.update({
            'comments': article.comments.filter(is_approved=True).order_by('-created_at'),
            'related_articles': Article.objects.filter(
                category=article.category,
                is_published=True
            ).exclude(pk=article.pk)[:3],
        })
        return context


class CategoryDetailView(DetailView):
    """
    Category detail showing books and articles in that category
    """
    model = Category
    template_name = 'cbv_practice/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        context.update({
            'books': category.books.filter(is_available=True)[:12],
            'articles': category.articles.filter(is_published=True)[:6],
            'total_books': category.books.filter(is_available=True).count(),
            'total_articles': category.articles.filter(is_published=True).count(),
        })
        return context


# =============================================================================
# 6. ASYNCHRONOUS CLASS-BASED VIEWS
# =============================================================================

class AsyncView(View):
    """
    Asynchronous view example from Django documentation
    Shows how to use async/await in class-based views
    """
    
    async def get(self, request, *args, **kwargs):
        # Simulate async operation (like API call or database query)
        await asyncio.sleep(1)
        
        # Get some data asynchronously
        book_count = await self._get_book_count_async()
        
        return JsonResponse({
            'message': 'Hello from async class-based view!',
            'book_count': book_count,
            'processed_at': timezone.now().isoformat(),
            'note': 'This response was generated asynchronously'
        })
    
    async def _get_book_count_async(self):
        """Simulate async database operation"""
        await asyncio.sleep(0.5)  # Simulate async database call
        from django.db import models
        from asgiref.sync import sync_to_async
        return await sync_to_async(Book.objects.count)()


class AsyncBookStatsView(View):
    """
    More complex async view with multiple async operations
    """
    
    async def get(self, request, *args, **kwargs):
        # Perform multiple async operations concurrently
        stats = await self._gather_stats_async()
        
        return JsonResponse({
            'stats': stats,
            'timestamp': timezone.now().isoformat(),
            'note': 'Statistics gathered asynchronously'
        })
    
    async def _gather_stats_async(self):
        """Gather various statistics asynchronously"""
        # Simulate multiple async database calls
        tasks = [
            self._count_books_async(),
            self._count_authors_async(),
            self._count_articles_async(),
            self._get_recent_books_async()
        ]
        
        book_count, author_count, article_count, recent_books = await asyncio.gather(*tasks)
        
        return {
            'total_books': book_count,
            'total_authors': author_count,
            'total_articles': article_count,
            'recent_books_count': len(recent_books),
            'recent_book_titles': [book['title'] for book in recent_books]
        }
    
    async def _count_books_async(self):
        await asyncio.sleep(0.1)
        from asgiref.sync import sync_to_async
        return await sync_to_async(Book.objects.count)()
    
    async def _count_authors_async(self):
        await asyncio.sleep(0.1)
        from asgiref.sync import sync_to_async
        return await sync_to_async(Author.objects.count)()
    
    async def _count_articles_async(self):
        await asyncio.sleep(0.1)
        from asgiref.sync import sync_to_async
        return await sync_to_async(lambda: Article.objects.filter(is_published=True).count)()
    
    async def _get_recent_books_async(self):
        await asyncio.sleep(0.2)
        from asgiref.sync import sync_to_async
        books = await sync_to_async(list)(
            Book.objects.filter(
                publication_date__gte=timezone.now().date() - timedelta(days=30)
            ).values('title', 'publication_date')[:5]
        )
        return books


# =============================================================================
# 7. ADVANCED PATTERNS AND MIXINS
# =============================================================================

class MultipleObjectMixin:
    """
    Custom mixin for views that work with multiple objects
    """
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_name'] = self.__class__.__name__
        context['timestamp'] = timezone.now()
        return context


class SearchMixin:
    """
    Mixin to add search functionality to ListView
    """
    search_fields = []
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        
        if search_query and self.search_fields:
            search_filter = Q()
            for field in self.search_fields:
                search_filter |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(search_filter)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class BreadcrumbMixin:
    """
    Mixin to add breadcrumb navigation
    """
    breadcrumbs = []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context
    
    def get_breadcrumbs(self):
        return self.breadcrumbs


class EnhancedBookListView(SearchMixin, BreadcrumbMixin, ListView):
    """
    Enhanced book list view using multiple mixins
    """
    model = Book
    template_name = 'cbv_practice/enhanced_book_list.html'
    context_object_name = 'books'
    paginate_by = 12
    search_fields = ['title', 'description', 'authors__name']
    breadcrumbs = [
        ('Home', 'cbv_practice:home'),
        ('Books', None),
    ]
    
    def get_queryset(self):
        return super().get_queryset().filter(is_available=True).select_related('category')


# =============================================================================
# 8. FORM HANDLING WITH CLASS-BASED VIEWS (Preview for next topic)
# =============================================================================

class CommentForm(ModelForm):
    """
    Simple form for adding comments to articles
    """
    class Meta:
        model = Comment
        fields = ['author_name', 'author_email', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
            'author_name': forms.TextInput(attrs={'placeholder': 'Your name'}),
            'author_email': forms.EmailInput(attrs={'placeholder': 'your.email@example.com'}),
        }


class ArticleCommentView(FormView):
    """
    Form view for adding comments to articles
    """
    form_class = CommentForm
    template_name = 'cbv_practice/add_comment.html'
    
    def get_success_url(self):
        return reverse('cbv_practice:article-detail', 
                      kwargs={'slug': self.kwargs['slug']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['article'] = get_object_or_404(Article, slug=self.kwargs['slug'])
        return context
    
    def form_valid(self, form):
        article = get_object_or_404(Article, slug=self.kwargs['slug'])
        comment = form.save(commit=False)
        comment.article = article
        comment.save()
        messages.success(self.request, 'Your comment has been submitted for review.')
        return super().form_valid(form)


# =============================================================================
# 9. UTILITY VIEWS
# =============================================================================

class StatsView(TemplateView):
    """
    Statistics dashboard showing various metrics
    """
    template_name = 'cbv_practice/stats.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate various statistics
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        context.update({
            'total_books': Book.objects.count(),
            'available_books': Book.objects.filter(is_available=True).count(),
            'total_authors': Author.objects.count(),
            'total_articles': Article.objects.filter(is_published=True).count(),
            'total_categories': Category.objects.count(),
            'recent_books': Book.objects.filter(
                created_at__gte=thirty_days_ago
            ).count(),
            'popular_books': Book.objects.filter(
                is_available=True
            ).order_by('-created_at')[:5],
            'active_authors': Author.objects.annotate(
                recent_books=Count('books', filter=Q(books__created_at__gte=thirty_days_ago))
            ).filter(recent_books__gt=0).count(),
            'categories_with_stats': Category.objects.annotate(
                book_count=Count('books', filter=Q(books__is_available=True)),
                article_count=Count('articles', filter=Q(articles__is_published=True))
            ).order_by('-book_count')[:10]
        })
        return context
