"""
Custom context processors for templates_practice app.
Following Django 5.2 documentation examples.
"""
from django.conf import settings
from django.utils import timezone
from .models import Category, Tag, Post, Newsletter
import datetime


def site_settings(request):
    """Add site-wide settings to template context."""
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Django Templates Practice'),
        'SITE_DESCRIPTION': getattr(settings, 'SITE_DESCRIPTION', 'Learning Django Templates'),
        'SITE_KEYWORDS': getattr(settings, 'SITE_KEYWORDS', 'django, templates, python'),
        'SITE_AUTHOR': getattr(settings, 'SITE_AUTHOR', 'Django Developer'),
        'CURRENT_YEAR': datetime.date.today().year,
        'DEBUG': settings.DEBUG,
    }


def navigation_data(request):
    """Add navigation data to template context."""
    return {
        'nav_categories': Category.objects.filter(is_active=True)[:10],
        'nav_tags': Tag.objects.all()[:15],
    }


def site_statistics(request):
    """Add site statistics to template context."""
    return {
        'stats': {
            'total_posts': Post.objects.filter(status=Post.PUBLISHED).count(),
            'total_categories': Category.objects.filter(is_active=True).count(),
            'total_tags': Tag.objects.count(),
            'total_subscribers': Newsletter.objects.filter(is_active=True).count(),
            'featured_posts_count': Post.objects.filter(
                status=Post.PUBLISHED, 
                featured=True
            ).count(),
        }
    }


def user_context(request):
    """Add user-specific context."""
    context = {
        'is_authenticated': request.user.is_authenticated,
    }
    
    if request.user.is_authenticated:
        context.update({
            'user_full_name': request.user.get_full_name() or request.user.username,
            'user_initials': ''.join([name[0].upper() for name in request.user.get_full_name().split()]) 
                           if request.user.get_full_name() else request.user.username[0].upper(),
        })
        
        # Check if user has author profile
        try:
            author = request.user.author
            context.update({
                'user_author': author,
                'user_posts_count': author.posts.filter(status=Post.PUBLISHED).count(),
                'user_draft_count': author.posts.filter(status=Post.DRAFT).count(),
            })
        except:
            context.update({
                'user_author': None,
                'user_posts_count': 0,
                'user_draft_count': 0,
            })
    
    return context


def request_data(request):
    """Add request-specific data to template context."""
    return {
        'current_url': request.path,
        'current_url_name': request.resolver_match.url_name if request.resolver_match else '',
        'query_params': request.GET,
        'is_ajax': request.headers.get('X-Requested-With') == 'XMLHttpRequest',
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'is_mobile': 'Mobile' in request.META.get('HTTP_USER_AGENT', ''),
    }


def datetime_context(request):
    """Add datetime-related context."""
    now = timezone.now()
    return {
        'now': now,
        'today': now.date(),
        'current_month': now.strftime('%B'),
        'current_year': now.year,
        'timestamp': now.timestamp(),
    }


def theme_context(request):
    """Add theme-related context."""
    # Get theme from session or default
    theme = request.session.get('theme', 'light')
    
    return {
        'current_theme': theme,
        'theme_options': ['light', 'dark', 'auto'],
        'is_dark_theme': theme == 'dark',
    }


def recent_activity(request):
    """Add recent activity to template context."""
    recent_posts = Post.objects.filter(
        status=Post.PUBLISHED
    ).order_by('-published_at')[:5]
    
    recent_categories = Category.objects.filter(
        is_active=True,
        posts__status=Post.PUBLISHED
    ).distinct().order_by('-posts__published_at')[:5]
    
    return {
        'recent_posts': recent_posts,
        'recent_categories': recent_categories,
    }


def featured_content(request):
    """Add featured content to template context."""
    return {
        'featured_posts': Post.objects.filter(
            status=Post.PUBLISHED,
            featured=True
        )[:3],
        'hero_post': Post.objects.filter(
            status=Post.PUBLISHED,
            featured=True
        ).first(),
    }


def breadcrumb_data(request):
    """Add breadcrumb data based on current URL."""
    breadcrumbs = [
        {'name': 'Home', 'url': '/templates_practice/'}
    ]
    
    url_name = request.resolver_match.url_name if request.resolver_match else ''
    
    if 'category' in url_name:
        breadcrumbs.append({'name': 'Categories', 'url': '/templates_practice/categories/'})
    elif 'tag' in url_name:
        breadcrumbs.append({'name': 'Tags', 'url': '/templates_practice/tags/'})
    elif 'post' in url_name:
        breadcrumbs.append({'name': 'Posts', 'url': '/templates_practice/posts/'})
    elif 'author' in url_name:
        breadcrumbs.append({'name': 'Authors', 'url': '/templates_practice/authors/'})
    
    return {
        'auto_breadcrumbs': breadcrumbs
    }


def search_context(request):
    """Add search-related context."""
    search_query = request.GET.get('q', '')
    
    context = {
        'search_query': search_query,
        'has_search': bool(search_query),
    }
    
    if search_query:
        # Add search suggestions or related terms
        context.update({
            'search_suggestions': [
                'django templates',
                'template filters',
                'template tags',
                'context processors',
            ]
        })
    
    return context
