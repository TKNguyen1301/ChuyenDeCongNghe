from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, generics, status
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated

from .models import Post, UserProfile, UserFeed
from .serializers import PostSerializer, UserProfileSerializer, UserFeedSerializer, UserSerializer


# Example 1: UserViewSet with cache_page and vary_on_cookie (from documentation)
class UserViewSet(viewsets.ViewSet):
    """
    ViewSet demonstrating cache_page with vary_on_cookie.
    From DRF documentation: cache requested url for each user for 2 hours.
    """
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 60 * 2))  # Cache for 2 hours
    @method_decorator(vary_on_cookie)
    def list(self, request, format=None):
        """List users with cached response varying by cookie."""
        # Simulate getting user feed
        content = {
            "user_feed": self.get_user_feed(request.user),
            "cached_at": timezone.now().isoformat(),
            "cache_info": "Cached for 2 hours, varies by cookie"
        }
        return Response(content)

    def get_user_feed(self, user):
        """Simulate getting user-specific feed data."""
        # In a real application, this would be expensive database queries
        feed_items = UserFeed.objects.filter(user=user)[:5]
        return UserFeedSerializer(feed_items, many=True).data


# Example 2: ProfileView with cache_page and vary_on_headers (from documentation)
class ProfileView(APIView):
    """
    APIView demonstrating cache_page with vary_on_headers.
    From DRF documentation: cache requested url for each user for 2 hours based on Authorization header.
    """
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 60 * 2))  # Cache for 2 hours
    @method_decorator(vary_on_headers("Authorization"))
    def get(self, request, format=None):
        """Get user profile with cached response varying by Authorization header."""
        content = {
            "user_feed": self.get_user_feed(request.user),
            "user_profile": self.get_user_profile(request.user),
            "cached_at": timezone.now().isoformat(),
            "cache_info": "Cached for 2 hours, varies by Authorization header"
        }
        return Response(content)

    def get_user_feed(self, user):
        """Get user feed data."""
        feed_items = UserFeed.objects.filter(user=user)[:3]
        return UserFeedSerializer(feed_items, many=True).data

    def get_user_profile(self, user):
        """Get user profile data."""
        try:
            profile = user.profile
            return UserProfileSerializer(profile).data
        except UserProfile.DoesNotExist:
            return {"bio": "", "location": "", "birth_date": None, "avatar": ""}


# Example 3: PostView with simple cache_page (from documentation)
class PostView(APIView):
    """
    APIView demonstrating simple cache_page without vary decorators.
    From DRF documentation: cache page for the requested url.
    """

    @method_decorator(cache_page(60 * 60 * 2))  # Cache for 2 hours
    def get(self, request, format=None):
        """Get post content with cached response."""
        content = {
            "title": "Post title",
            "body": "Post content",
            "cached_at": timezone.now().isoformat(),
            "cache_info": "Cached for 2 hours, same for all users"
        }
        return Response(content)


# Additional examples for comprehensive caching demonstration

class CachedPostListView(generics.ListAPIView):
    """
    List view with caching for post listings.
    """
    queryset = Post.objects.filter(published=True)
    serializer_class = PostSerializer

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def get(self, request, *args, **kwargs):
        """Get cached list of posts."""
        return super().get(request, *args, **kwargs)


class UserSpecificCachedView(APIView):
    """
    View demonstrating user-specific caching with manual cache control.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """Get user-specific data with manual caching."""
        cache_key = f"user_data_{request.user.id}"
        cached_data = cache.get(cache_key)

        if cached_data is None:
            # Cache miss - generate data
            user_data = {
                "user": UserSerializer(request.user).data,
                "recent_posts": PostSerializer(
                    Post.objects.filter(author=request.user)[:5], 
                    many=True
                ).data,
                "feed_count": UserFeed.objects.filter(user=request.user).count(),
                "generated_at": timezone.now().isoformat(),
                "cache_info": "Manually cached for 10 minutes"
            }
            # Cache for 10 minutes
            cache.set(cache_key, user_data, 60 * 10)
            cached_data = user_data
            cached_data["cache_status"] = "MISS"
        else:
            cached_data["cache_status"] = "HIT"

        return Response(cached_data)


class ConditionalCacheView(APIView):
    """
    View demonstrating conditional caching based on request parameters.
    """

    def get(self, request, format=None):
        """Get data with conditional caching."""
        category = request.query_params.get('category', 'all')
        cache_key = f"posts_by_category_{category}"
        
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            # Generate data based on category
            if category == 'all':
                posts = Post.objects.filter(published=True)
            else:
                # For demo, we'll just filter by author username containing category
                posts = Post.objects.filter(
                    published=True,
                    author__username__icontains=category
                )
            
            data = {
                "category": category,
                "posts": PostSerializer(posts[:10], many=True).data,
                "total_count": posts.count(),
                "generated_at": timezone.now().isoformat(),
                "cache_info": f"Cached for category '{category}' for 3 minutes"
            }
            
            # Cache for 3 minutes
            cache.set(cache_key, data, 60 * 3)
            data["cache_status"] = "MISS"
        else:
            cached_data["cache_status"] = "HIT"
            data = cached_data

        return Response(data)


class CacheInvalidationView(APIView):
    """
    View demonstrating cache invalidation.
    """
    
    def post(self, request, format=None):
        """Clear specific cache keys."""
        keys_to_clear = request.data.get('cache_keys', [])
        pattern = request.data.get('pattern', None)
        
        cleared_keys = []
        
        if keys_to_clear:
            for key in keys_to_clear:
                cache.delete(key)
                cleared_keys.append(key)
        
        if pattern:
            # For demonstration - in production you'd want a more sophisticated pattern matching
            # This is a simple example that clears user-specific caches
            if pattern == 'user_*':
                for user in User.objects.all():
                    key = f"user_data_{user.id}"
                    cache.delete(key)
                    cleared_keys.append(key)
        
        return Response({
            "message": f"Cleared {len(cleared_keys)} cache keys",
            "cleared_keys": cleared_keys,
            "timestamp": timezone.now().isoformat()
        })

    def delete(self, request, format=None):
        """Clear all cache."""
        cache.clear()
        return Response({
            "message": "All cache cleared",
            "timestamp": timezone.now().isoformat()
        })


class CacheStatsView(APIView):
    """
    View to inspect cache status and provide cache statistics.
    """
    
    def get(self, request, format=None):
        """Get cache statistics and test cache functionality."""
        # Test cache functionality
        test_key = "cache_test"
        test_value = {"test": True, "timestamp": timezone.now().isoformat()}
        
        # Set and immediately get to test cache
        cache.set(test_key, test_value, 60)
        retrieved_value = cache.get(test_key)
        
        # Check some specific cache keys
        sample_keys = [
            "user_data_1",
            "posts_by_category_all",
            "cache_test"
        ]
        
        key_status = {}
        for key in sample_keys:
            value = cache.get(key)
            key_status[key] = "EXISTS" if value is not None else "NOT_FOUND"
        
        return Response({
            "cache_backend": str(cache),
            "test_cache_working": retrieved_value == test_value,
            "sample_key_status": key_status,
            "cache_info": {
                "default_timeout": getattr(cache, 'default_timeout', 'N/A'),
                "backend_class": cache.__class__.__name__
            },
            "timestamp": timezone.now().isoformat()
        })


# ViewSet with multiple cached actions
class CachedPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet demonstrating caching on different actions.
    """
    queryset = Post.objects.filter(published=True)
    serializer_class = PostSerializer

    @method_decorator(cache_page(60 * 5))  # Cache list for 5 minutes
    def list(self, request, *args, **kwargs):
        """Cached list of posts."""
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))  # Cache individual posts for 15 minutes
    def retrieve(self, request, *args, **kwargs):
        """Cached individual post retrieval."""
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 10))  # Cache custom action for 10 minutes
    def recent(self, request):
        """Get recent posts (custom cached action)."""
        recent_posts = Post.objects.filter(
            published=True,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')[:5]
        
        serializer = self.get_serializer(recent_posts, many=True)
        return Response({
            "recent_posts": serializer.data,
            "cached_at": timezone.now().isoformat(),
            "cache_info": "Recent posts cached for 10 minutes"
        })

    @action(detail=True, methods=['get'])
    @method_decorator(cache_page(60 * 20))  # Cache related posts for 20 minutes
    def related(self, request, pk=None):
        """Get posts related to this post (by same author)."""
        post = self.get_object()
        related_posts = Post.objects.filter(
            author=post.author,
            published=True
        ).exclude(id=post.id)[:3]
        
        serializer = self.get_serializer(related_posts, many=True)
        return Response({
            "post_id": post.id,
            "post_title": post.title,
            "related_posts": serializer.data,
            "cached_at": timezone.now().isoformat(),
            "cache_info": "Related posts cached for 20 minutes"
        })