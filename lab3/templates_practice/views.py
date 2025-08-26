"""
Django Templates Practice Views
Following Django 5.2 documentation examples.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, TemplateView, CreateView, UpdateView
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.template.loader import render_to_string, get_template
from django.template import Context, Template
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
import json

from .models import Post, Category, Tag, Author, Comment, Newsletter, TemplateExample
from .forms import CommentForm, NewsletterForm, PostForm


# BASIC TEMPLATE VIEWS
class HomeView(TemplateView):
    """Home page demonstrating basic template features."""
    template_name = 'templates_practice/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Featured posts
        featured_posts = Post.objects.filter(
            status=Post.PUBLISHED,
            featured=True
        )[:3]
        
        # Recent posts
        recent_posts = Post.objects.filter(
            status=Post.PUBLISHED
        )[:6]
        
        # Categories with post counts
        categories = Category.objects.filter(is_active=True).annotate(
            post_count=Count('posts', filter=Q(posts__status=Post.PUBLISHED))
        ).filter(post_count__gt=0)[:8]
        
        # Popular tags
        popular_tags = Tag.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status=Post.PUBLISHED))
        ).filter(post_count__gt=0).order_by('-post_count')[:10]
        
        context.update({
            'featured_posts': featured_posts,
            'recent_posts': recent_posts,
            'categories': categories,
            'popular_tags': popular_tags,
            'page_title': 'Django Templates Practice',
            'page_description': 'Learning Django Templates with practical examples',
        })
        
        return context


class PostListView(ListView):
    """Post list view with filtering and pagination."""
    model = Post
    template_name = 'templates_practice/posts/list.html'
    context_object_name = 'posts'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Post.objects.filter(status=Post.PUBLISHED).select_related(
            'author__user', 'category'
        ).prefetch_related('tags')
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by tag
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query)
            )
        
        # Ordering
        order_by = self.request.GET.get('order', '-published_at')
        if order_by in ['-published_at', 'published_at', '-view_count', 'title']:
            queryset = queryset.order_by(order_by)
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'current_category': self.request.GET.get('category'),
            'current_tag': self.request.GET.get('tag'),
            'search_query': self.request.GET.get('q', ''),
            'current_order': self.request.GET.get('order', '-published_at'),
            'page_title': 'All Posts',
        })
        
        return context


class PostDetailView(DetailView):
    """Post detail view demonstrating template inheritance and includes."""
    model = Post
    template_name = 'templates_practice/posts/detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Post.objects.filter(status=Post.PUBLISHED).select_related(
            'author__user', 'category'
        ).prefetch_related('tags', 'comments__replies')
    
    def get_object(self):
        obj = super().get_object()
        # Increment view count
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        
        # Related posts
        related_posts = post.get_related_posts(limit=4)
        
        # Comments
        comments = post.comments.filter(
            is_approved=True,
            is_spam=False,
            parent=None
        ).select_related('post').prefetch_related('replies')
        
        context.update({
            'related_posts': related_posts,
            'comments': comments,
            'comment_form': CommentForm(),
            'page_title': post.title,
            'page_description': post.excerpt,
        })
        
        return context


class CategoryDetailView(DetailView):
    """Category detail view with posts."""
    model = Category
    template_name = 'templates_practice/categories/detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        
        # Category posts with pagination
        posts = category.posts.filter(status=Post.PUBLISHED).select_related(
            'author__user'
        ).prefetch_related('tags')
        
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context.update({
            'posts': page_obj,
            'page_obj': page_obj,
            'page_title': f'Category: {category.name}',
            'page_description': category.description,
        })
        
        return context


class TagDetailView(DetailView):
    """Tag detail view with posts."""
    model = Tag
    template_name = 'templates_practice/tags/detail.html'
    context_object_name = 'tag'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = self.object
        
        # Tag posts with pagination
        posts = tag.posts.filter(status=Post.PUBLISHED).select_related(
            'author__user', 'category'
        )
        
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context.update({
            'posts': page_obj,
            'page_obj': page_obj,
            'page_title': f'Tag: {tag.name}',
        })
        
        return context


class AuthorDetailView(DetailView):
    """Author detail view with posts."""
    model = Author
    template_name = 'templates_practice/authors/detail.html'
    context_object_name = 'author'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.object
        
        # Author posts with pagination
        posts = author.posts.filter(status=Post.PUBLISHED).select_related(
            'category'
        ).prefetch_related('tags')
        
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context.update({
            'posts': page_obj,
            'page_obj': page_obj,
            'page_title': f'Author: {author.full_name}',
            'page_description': author.bio,
        })
        
        return context


# TEMPLATE ENGINE DEMONSTRATION VIEWS
class TemplateEngineView(TemplateView):
    """Demonstrate template engine features."""
    template_name = 'templates_practice/examples/template_engine.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Demonstrate context data
        context.update({
            'page_title': 'Template Engine Examples',
            'demo_string': 'Hello, Django Templates!',
            'demo_number': 42,
            'demo_list': ['apple', 'banana', 'cherry', 'date'],
            'demo_dict': {
                'name': 'Django',
                'version': '5.2',
                'language': 'Python',
                'framework_type': 'Web'
            },
            'demo_boolean': True,
            'demo_object': {
                'title': 'Sample Object',
                'description': 'This is a sample object for template demonstration',
                'created_at': timezone.now(),
                'nested': {
                    'value': 'Nested value',
                    'count': 10
                }
            },
            'html_content': '<strong>Bold Text</strong> and <em>italic text</em>',
            'markdown_content': '# Heading\n\nThis is **bold** and *italic* text.',
        })
        
        return context


class TemplateFiltersView(TemplateView):
    """Demonstrate template filters."""
    template_name = 'templates_practice/examples/filters.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'page_title': 'Template Filters Examples',
            'demo_date': timezone.now(),
            'demo_text': 'The Quick Brown Fox Jumps Over The Lazy Dog',
            'demo_long_text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. ' * 10,
            'demo_number': 1234567.89,
            'demo_html': '<script>alert("XSS")</script><p>Safe HTML</p>',
            'demo_url': 'https://example.com/path/to/page',
            'demo_list': list(range(1, 21)),
            'demo_empty_value': None,
            'demo_rating': 4.3,
            'demo_percentage': 0.85,
        })
        
        return context


class TemplateTagsView(TemplateView):
    """Demonstrate template tags."""
    template_name = 'templates_practice/examples/tags.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Sample data for tag demonstrations
        posts_sample = Post.objects.filter(status=Post.PUBLISHED)[:5]
        
        context.update({
            'page_title': 'Template Tags Examples',
            'posts_sample': posts_sample,
            'user_list': ['Alice', 'Bob', 'Charlie', 'Diana'],
            'nested_list': [
                ['A', 'B', 'C'],
                ['D', 'E', 'F'],
                ['G', 'H', 'I']
            ],
            'conditions': {
                'is_morning': timezone.now().hour < 12,
                'is_weekend': timezone.now().weekday() >= 5,
                'is_authenticated': self.request.user.is_authenticated,
            },
            'demo_count': 15,
            'demo_score': 85,
        })
        
        return context


class TemplateInheritanceView(TemplateView):
    """Demonstrate template inheritance."""
    template_name = 'templates_practice/examples/inheritance.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'page_title': 'Template Inheritance Example',
            'page_description': 'This page demonstrates Django template inheritance patterns',
            'sidebar_content': 'This is sidebar content passed from the view',
            'extra_css': ['custom.css', 'inheritance.css'],
            'extra_js': ['custom.js', 'inheritance.js'],
        })
        
        return context


class CustomTagsView(TemplateView):
    """Demonstrate custom template tags."""
    template_name = 'templates_practice/examples/custom_tags.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'page_title': 'Custom Template Tags Examples',
            'demo_text': 'this text will be processed by custom tags',
            'search_term': 'Django',
            'search_text': 'Django is a high-level Python web framework that encourages rapid development.',
            'user_rating': 4.5,
            'completion_percentage': 75,
        })
        
        return context


# FORM HANDLING VIEWS
@require_http_methods(["POST"])
def add_comment(request, post_slug):
    """Add comment to post via AJAX."""
    post = get_object_or_404(Post, slug=post_slug, status=Post.PUBLISHED)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            
            # Render comment HTML
            comment_html = render_to_string(
                'templates_practice/includes/comment.html',
                {'comment': comment},
                request=request
            )
            
            return JsonResponse({
                'success': True,
                'comment_html': comment_html,
                'message': 'Comment added successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return redirect('templates_practice:post_detail', slug=post_slug)


@require_http_methods(["POST"])
def subscribe_newsletter(request):
    """Subscribe to newsletter via AJAX."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = NewsletterForm(request.POST)
        
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Successfully subscribed to newsletter!'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return redirect('templates_practice:home')


# TEMPLATE EXAMPLES VIEWS
class TemplateExamplesListView(ListView):
    """List all template examples."""
    model = TemplateExample
    template_name = 'templates_practice/examples/list.html'
    context_object_name = 'examples'
    paginate_by = 10
    
    def get_queryset(self):
        return TemplateExample.objects.filter(is_active=True)


class TemplateExampleDetailView(DetailView):
    """Show individual template example."""
    model = TemplateExample
    template_name = 'templates_practice/examples/example_detail.html'
    context_object_name = 'example'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        example = self.object
        
        # Render the example template
        try:
            template = Template(example.template_code)
            rendered_output = template.render(Context(example.demo_data))
            context['rendered_output'] = rendered_output
        except Exception as e:
            context['render_error'] = str(e)
        
        return context


# SEARCH VIEWS
def search_view(request):
    """Advanced search functionality."""
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    tag_filter = request.GET.get('tag', '')
    author_filter = request.GET.get('author', '')
    
    results = Post.objects.filter(status=Post.PUBLISHED)
    
    if query:
        results = results.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(author__user__first_name__icontains=query) |
            Q(author__user__last_name__icontains=query)
        )
    
    if category_filter:
        results = results.filter(category__slug=category_filter)
    
    if tag_filter:
        results = results.filter(tags__slug=tag_filter)
    
    if author_filter:
        results = results.filter(author__pk=author_filter)
    
    results = results.select_related(
        'author__user', 'category'
    ).prefetch_related('tags').distinct()
    
    # Pagination
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'results': page_obj,
        'page_obj': page_obj,
        'total_results': paginator.count,
        'categories': Category.objects.filter(is_active=True),
        'tags': Tag.objects.all()[:20],
        'authors': Author.objects.all(),
        'page_title': f'Search Results for "{query}"' if query else 'Search',
    }
    
    return render(request, 'templates_practice/search/results.html', context)


# AJAX VIEWS
def load_more_posts(request):
    """Load more posts via AJAX."""
    page = int(request.GET.get('page', 1))
    category_slug = request.GET.get('category')
    
    posts = Post.objects.filter(status=Post.PUBLISHED)
    
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    posts = posts.select_related('author__user', 'category')
    
    paginator = Paginator(posts, 6)
    page_obj = paginator.get_page(page)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        posts_html = render_to_string(
            'templates_practice/includes/post_cards.html',
            {'posts': page_obj},
            request=request
        )
        
        return JsonResponse({
            'success': True,
            'posts_html': posts_html,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None
        })
    
    return JsonResponse({'success': False})


# TEMPLATE LOADER EXAMPLES
def template_loader_examples(request):
    """Demonstrate template loading methods."""
    context = {
        'page_title': 'Template Loader Examples',
        'demo_data': {
            'name': 'Django',
            'version': '5.2',
            'features': ['Templates', 'ORM', 'Admin', 'Authentication']
        }
    }
    
    # Example 1: Using get_template
    template = get_template('templates_practice/examples/loader_demo.html')
    rendered_template = template.render(context, request)
    
    # Example 2: Using render_to_string
    rendered_string = render_to_string(
        'templates_practice/examples/loader_demo.html',
        context,
        request=request
    )
    
    context.update({
        'rendered_template': rendered_template,
        'rendered_string': rendered_string,
        'templates_equal': rendered_template == rendered_string,
    })
    
    return render(request, 'templates_practice/examples/template_loading.html', context)


# CONTEXT PROCESSOR DEMO
class ContextProcessorView(TemplateView):
    """Demonstrate context processors."""
    template_name = 'templates_practice/examples/context_processors.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'page_title': 'Context Processors Demo',
            'view_specific_data': 'This data comes from the view',
            'local_timestamp': timezone.now(),
        })
        
        return context
