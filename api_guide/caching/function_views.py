from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Post, UserFeed, UserProfile
from .serializers import PostSerializer, UserFeedSerializer, UserSerializer


# Example from DRF documentation: function-based view with cache_page and vary_on_cookie
@cache_page(60 * 15)  # Cache for 15 minutes
@vary_on_cookie
@api_view(["GET"])
def get_user_list(request):
    """
    Function-based view from DRF documentation.
    Cache for 15 minutes, vary by cookie.
    """
    if request.user.is_authenticated:
        content = {
            "user_feed": get_user_feed_data(request.user),
            "cached_at": timezone.now().isoformat(),
            "cache_info": "Cached for 15 minutes, varies by cookie"
        }
    else:
        content = {
            "message": "Please authenticate to see user feed",
            "cached_at": timezone.now().isoformat(),
            "cache_info": "Cached for 15 minutes, varies by cookie"
        }
    return Response(content)


# Additional function-based view examples

@cache_page(60 * 5)  # Cache for 5 minutes
@api_view(["GET"])
def get_public_posts(request):
    """
    Get public posts - cached for all users.
    """
    posts = Post.objects.filter(published=True)[:10]
    content = {
        "posts": PostSerializer(posts, many=True).data,
        "total_count": Post.objects.filter(published=True).count(),
        "cached_at": timezone.now().isoformat(),
        "cache_info": "Cached for 5 minutes, same for all users"
    }
    return Response(content)


@cache_page(60 * 10)  # Cache for 10 minutes
@vary_on_headers("Authorization")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_dashboard(request):
    """
    Get user dashboard data - cached per user based on Authorization header.
    """
    user = request.user
    content = {
        "user": UserSerializer(user).data,
        "recent_posts": PostSerializer(
            Post.objects.filter(author=user)[:5], 
            many=True
        ).data,
        "feed_items": UserFeedSerializer(
            UserFeed.objects.filter(user=user)[:5], 
            many=True
        ).data,
        "cached_at": timezone.now().isoformat(),
        "cache_info": "Cached for 10 minutes, varies by Authorization header"
    }
    return Response(content)


@cache_page(60 * 3)  # Cache for 3 minutes
@vary_on_cookie
@api_view(["GET"])
def get_user_stats(request):
    """
    Get user statistics - varies by cookie.
    """
    if request.user.is_authenticated:
        user = request.user
        stats = {
            "username": user.username,
            "posts_count": Post.objects.filter(author=user).count(),
            "published_posts_count": Post.objects.filter(author=user, published=True).count(),
            "feed_items_count": UserFeed.objects.filter(user=user).count(),
            "join_date": user.date_joined.isoformat(),
        }
    else:
        stats = {
            "message": "Please authenticate to see your statistics"
        }
    
    content = {
        "stats": stats,
        "cached_at": timezone.now().isoformat(),
        "cache_info": "Cached for 3 minutes, varies by cookie"
    }
    return Response(content)


@api_view(["GET"])
def get_cached_post_by_id(request, post_id):
    """
    Get individual post with manual caching.
    """
    cache_key = f"post_{post_id}"
    cached_post = cache.get(cache_key)
    
    if cached_post is None:
        try:
            post = Post.objects.get(id=post_id, published=True)
            post_data = {
                "post": PostSerializer(post).data,
                "author": UserSerializer(post.author).data,
                "cached_at": timezone.now().isoformat(),
                "cache_info": "Manually cached for 8 minutes"
            }
            # Cache for 8 minutes
            cache.set(cache_key, post_data, 60 * 8)
            post_data["cache_status"] = "MISS"
            return Response(post_data)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        cached_post["cache_status"] = "HIT"
        return Response(cached_post)


@api_view(["GET"])
def get_posts_by_author(request, username):
    """
    Get posts by author with caching.
    """
    cache_key = f"posts_by_author_{username}"
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        try:
            author = User.objects.get(username=username)
            posts = Post.objects.filter(author=author, published=True)[:10]
            
            data = {
                "author": UserSerializer(author).data,
                "posts": PostSerializer(posts, many=True).data,
                "total_posts": Post.objects.filter(author=author, published=True).count(),
                "cached_at": timezone.now().isoformat(),
                "cache_info": f"Posts by {username} cached for 6 minutes"
            }
            
            # Cache for 6 minutes
            cache.set(cache_key, data, 60 * 6)
            data["cache_status"] = "MISS"
            return Response(data)
        except User.DoesNotExist:
            return Response(
                {"error": "Author not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        cached_data["cache_status"] = "HIT"
        return Response(cached_data)


@cache_page(60 * 20)  # Cache for 20 minutes
@api_view(["GET"])
def get_site_statistics(request):
    """
    Get site-wide statistics - cached for all users.
    """
    stats = {
        "total_users": User.objects.count(),
        "total_posts": Post.objects.count(),
        "published_posts": Post.objects.filter(published=True).count(),
        "total_feed_items": UserFeed.objects.count(),
        "recent_users": UserSerializer(
            User.objects.order_by('-date_joined')[:5], 
            many=True
        ).data,
    }
    
    content = {
        "site_stats": stats,
        "cached_at": timezone.now().isoformat(),
        "cache_info": "Site statistics cached for 20 minutes"
    }
    return Response(content)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def invalidate_user_cache(request):
    """
    Invalidate user-specific cache entries.
    """
    user = request.user
    
    # List of cache keys that might exist for this user
    cache_keys_to_clear = [
        f"user_data_{user.id}",
        f"posts_by_author_{user.username}",
    ]
    
    cleared_keys = []
    for key in cache_keys_to_clear:
        cache.delete(key)
        cleared_keys.append(key)
    
    return Response({
        "message": f"Cleared cache for user {user.username}",
        "cleared_keys": cleared_keys,
        "timestamp": timezone.now().isoformat()
    })


@api_view(["GET"])
def test_cache_performance(request):
    """
    Test cache performance by measuring cache hit vs miss times.
    """
    import time
    
    test_key = "performance_test"
    test_data = {
        "large_data": list(range(1000)),
        "timestamp": timezone.now().isoformat()
    }
    
    # Test cache miss (fresh data)
    cache.delete(test_key)
    start_time = time.time()
    cache.set(test_key, test_data, 60)
    miss_time = time.time() - start_time
    
    # Test cache hit
    start_time = time.time()
    cached_data = cache.get(test_key)
    hit_time = time.time() - start_time
    
    return Response({
        "cache_miss_time_ms": round(miss_time * 1000, 4),
        "cache_hit_time_ms": round(hit_time * 1000, 4),
        "speedup_factor": round(miss_time / hit_time, 2) if hit_time > 0 else "N/A",
        "data_size": len(str(test_data)),
        "cache_backend": str(cache),
        "timestamp": timezone.now().isoformat()
    })


# Helper function
def get_user_feed_data(user):
    """Helper function to get user feed data."""
    feed_items = UserFeed.objects.filter(user=user)[:5]
    return UserFeedSerializer(feed_items, many=True).data