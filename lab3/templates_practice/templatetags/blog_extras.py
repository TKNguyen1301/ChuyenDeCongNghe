"""
Custom template tags and filters for templates_practice app.
Following Django 5.2 documentation examples.
"""
import re
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.template.defaultfilters import stringfilter
from django.utils.timesince import timesince
from django.utils import timezone
from django.urls import reverse
from ..models import Post, Category, Tag
import random
import markdown

register = template.Library()


# SIMPLE FILTERS
@register.filter
@stringfilter
def cut(value, arg):
    """Removes all values of arg from the given string."""
    return value.replace(arg, '')


@register.filter
def lower(value):
    """Converts a string into all lowercase."""
    return value.lower()


@register.filter
def title_case(value):
    """Converts to title case."""
    return value.title()


@register.filter
def truncate_chars(value, length):
    """Truncates a string to a specified number of characters."""
    if len(value) <= length:
        return value
    return value[:length] + '...'


@register.filter
def word_count(value):
    """Returns the number of words in a string."""
    return len(value.split())


@register.filter
def reading_time(content, wpm=200):
    """Calculate reading time in minutes based on word count."""
    words = len(content.split())
    minutes = max(1, words // wpm)
    return f"{minutes} min read"


@register.filter
def percentage(value, total):
    """Calculate percentage."""
    try:
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def range_filter(value):
    """Create a range for template iteration."""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary using key."""
    return dictionary.get(key)


@register.filter
def smart_truncate(content, length=100):
    """Smart truncation that respects word boundaries."""
    if len(content) <= length:
        return content
    
    truncated = content[:length]
    last_space = truncated.rfind(' ')
    
    if last_space != -1:
        truncated = truncated[:last_space]
    
    return truncated + '...'


@register.filter
def time_ago(value):
    """Custom time ago filter."""
    if not value:
        return ''
    
    now = timezone.now()
    diff = now - value
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


@register.filter
def markdown_to_html(value):
    """Convert markdown to HTML."""
    return mark_safe(markdown.markdown(value))


@register.filter
def highlight_search(text, search_term):
    """Highlight search terms in text."""
    if not search_term:
        return text
    
    highlighted = re.sub(
        f'({re.escape(search_term)})',
        r'<mark>\1</mark>',
        text,
        flags=re.IGNORECASE
    )
    return mark_safe(highlighted)


@register.filter
def add_class(field, css_class):
    """Add CSS class to form field."""
    return field.as_widget(attrs={'class': css_class})


# SIMPLE TAGS
@register.simple_tag
def current_time(format_string):
    """Display current time with custom format."""
    return timezone.now().strftime(format_string)


@register.simple_tag
def random_post():
    """Get a random published post."""
    posts = Post.objects.filter(status=Post.PUBLISHED)
    if posts.exists():
        return random.choice(posts)
    return None


@register.simple_tag
def post_count_by_category(category_slug):
    """Count posts in a category."""
    try:
        category = Category.objects.get(slug=category_slug)
        return category.posts.filter(status=Post.PUBLISHED).count()
    except Category.DoesNotExist:
        return 0


@register.simple_tag
def site_stats():
    """Get site statistics."""
    return {
        'total_posts': Post.objects.filter(status=Post.PUBLISHED).count(),
        'total_categories': Category.objects.filter(is_active=True).count(),
        'total_tags': Tag.objects.count(),
        'featured_posts': Post.objects.filter(status=Post.PUBLISHED, featured=True).count(),
    }


@register.simple_tag
def url_replace(request, field, value):
    """Replace URL parameter while keeping others."""
    params = request.GET.copy()
    params[field] = value
    return params.urlencode()


@register.simple_tag(takes_context=True)
def active_link(context, url_name, exact=False):
    """Add 'active' class if current URL matches."""
    request = context['request']
    current_url = request.resolver_match.url_name
    
    if exact:
        return 'active' if current_url == url_name else ''
    else:
        return 'active' if url_name in current_url else ''


@register.simple_tag
def build_url(url_name, *args, **kwargs):
    """Build URL with arguments."""
    return reverse(url_name, args=args, kwargs=kwargs)


# INCLUSION TAGS
@register.inclusion_tag('templates_practice/tags/recent_posts.html')
def recent_posts(count=5):
    """Display recent posts widget."""
    posts = Post.objects.filter(status=Post.PUBLISHED)[:count]
    return {'posts': posts}


@register.inclusion_tag('templates_practice/tags/popular_posts.html')
def popular_posts(count=5):
    """Display popular posts widget."""
    posts = Post.objects.filter(
        status=Post.PUBLISHED
    ).order_by('-view_count')[:count]
    return {'posts': posts}


@register.inclusion_tag('templates_practice/tags/category_list.html')
def category_list():
    """Display category list with post counts."""
    categories = Category.objects.filter(is_active=True).prefetch_related('posts')
    category_data = []
    
    for category in categories:
        post_count = category.posts.filter(status=Post.PUBLISHED).count()
        if post_count > 0:
            category_data.append({
                'category': category,
                'post_count': post_count
            })
    
    return {'categories': category_data}


@register.inclusion_tag('templates_practice/tags/tag_cloud.html')
def tag_cloud(limit=20):
    """Display tag cloud."""
    tags = Tag.objects.prefetch_related('posts')[:limit]
    tag_data = []
    
    for tag in tags:
        post_count = tag.posts.filter(status=Post.PUBLISHED).count()
        if post_count > 0:
            # Calculate font size based on post count
            font_size = min(100 + (post_count * 10), 200)
            tag_data.append({
                'tag': tag,
                'post_count': post_count,
                'font_size': font_size
            })
    
    return {'tags': tag_data}


@register.inclusion_tag('templates_practice/tags/breadcrumb.html', takes_context=True)
def breadcrumb(context, *crumbs):
    """Generate breadcrumb navigation."""
    request = context['request']
    breadcrumbs = [
        {'name': 'Home', 'url': reverse('templates_practice:home')}
    ]
    
    for crumb in crumbs:
        if isinstance(crumb, dict):
            breadcrumbs.append(crumb)
        else:
            breadcrumbs.append({'name': str(crumb), 'url': None})
    
    return {
        'breadcrumbs': breadcrumbs,
        'request': request
    }


@register.inclusion_tag('templates_practice/tags/pagination_links.html', takes_context=True)
def pagination_links(context, page_obj):
    """Generate pagination links."""
    request = context['request']
    
    # Get query parameters except page
    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    
    return {
        'page_obj': page_obj,
        'query_params': params.urlencode(),
        'request': request
    }


@register.inclusion_tag('templates_practice/tags/social_share.html')
def social_share(post, request):
    """Generate social sharing buttons."""
    full_url = request.build_absolute_uri(post.get_absolute_url())
    
    return {
        'post': post,
        'full_url': full_url,
        'encoded_title': post.title.replace(' ', '%20'),
        'encoded_url': full_url.replace(':', '%3A').replace('/', '%2F')
    }


# ASSIGNMENT TAGS (using simple_tag)
@register.simple_tag
def get_featured_posts(count=3):
    """Get featured posts."""
    return Post.objects.filter(
        status=Post.PUBLISHED,
        featured=True
    )[:count]


@register.simple_tag
def get_posts_by_tag(tag_slug, count=5):
    """Get posts by tag."""
    try:
        tag = Tag.objects.get(slug=tag_slug)
        return tag.posts.filter(status=Post.PUBLISHED)[:count]
    except Tag.DoesNotExist:
        return Post.objects.none()


@register.simple_tag
def get_related_posts(post, count=3):
    """Get related posts."""
    return post.get_related_posts(count)


# TEMPLATE NODE TAGS (Advanced)
class CapitalizeNode(template.Node):
    """Custom template node for capitalization."""
    
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        output = self.nodelist.render(context)
        return output.upper()


@register.tag(name="capitalize")
def do_capitalize(parser, token):
    """
    Capitalizes everything between {% capitalize %} and {% endcapitalize %}.
    
    Usage:
    {% capitalize %}
        {{ some_variable }}
    {% endcapitalize %}
    """
    nodelist = parser.parse(('endcapitalize',))
    parser.delete_first_token()
    return CapitalizeNode(nodelist)


class SetVariableNode(template.Node):
    """Custom template node for setting variables."""
    
    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value
    
    def render(self, context):
        context[self.var_name] = self.var_value.resolve(context)
        return ''


@register.tag(name="set")
def do_set(parser, token):
    """
    Set a variable in template context.
    
    Usage:
    {% set my_var = "some value" %}
    {% set count = posts|length %}
    """
    try:
        # Split the tag contents
        tag_name, arg = token.contents.split(None, 1)
        var_name, var_value = arg.split('=', 1)
        var_name = var_name.strip()
        var_value = parser.compile_filter(var_value.strip())
    except ValueError:
        raise template.TemplateSyntaxError(
            f"'{token.contents.split()[0]}' tag requires format: "
            "{% set var_name = value %}"
        )
    
    return SetVariableNode(var_name, var_value)


# FILTERS WITH ARGUMENTS
@register.filter
def stars(rating, max_stars=5):
    """Generate star rating display."""
    full_stars = int(rating)
    half_star = 1 if rating - full_stars >= 0.5 else 0
    empty_stars = max_stars - full_stars - half_star
    
    star_html = '★' * full_stars
    if half_star:
        star_html += '☆'
    star_html += '☆' * empty_stars
    
    return mark_safe(f'<span class="stars" title="{rating}/{max_stars}">{star_html}</span>')


@register.filter
def badge(value, badge_type='primary'):
    """Generate Bootstrap badge."""
    return format_html(
        '<span class="badge badge-{}">{}</span>',
        badge_type,
        value
    )


@register.filter
def progress_bar(value, max_value=100):
    """Generate progress bar."""
    percentage = min(100, (value / max_value) * 100) if max_value > 0 else 0
    return format_html(
        '<div class="progress"><div class="progress-bar" style="width: {}%">{}</div></div>',
        percentage,
        f"{percentage:.1f}%"
    )


# Context-dependent tags
@register.simple_tag(takes_context=True)
def user_posts_count(context):
    """Get current user's post count."""
    request = context['request']
    if request.user.is_authenticated:
        try:
            author = request.user.author
            return author.posts.filter(status=Post.PUBLISHED).count()
        except:
            return 0
    return 0


@register.simple_tag(takes_context=True)
def is_bookmarked(context, post):
    """Check if post is bookmarked by current user."""
    request = context['request']
    if request.user.is_authenticated:
        # In a real app, you'd check bookmarks
        return random.choice([True, False])
    return False
