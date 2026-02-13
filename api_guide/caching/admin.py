from django.contrib import admin
from .models import Post, UserProfile, UserFeed


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published', 'created_at']
    list_filter = ['published', 'created_at', 'author']
    search_fields = ['title', 'body']
    date_hierarchy = 'created_at'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'birth_date']
    search_fields = ['user__username', 'bio', 'location']


@admin.register(UserFeed)
class UserFeedAdmin(admin.ModelAdmin):
    list_display = ['user', 'feed_type', 'created_at']
    list_filter = ['feed_type', 'created_at']
    search_fields = ['user__username', 'content']
    date_hierarchy = 'created_at'