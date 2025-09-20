"""
Django Admin Configuration for Templates Practice
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category, Tag, Author, Post, Comment, Newsletter, TemplateExample
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    list_display = ['name', 'slug', 'post_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    def post_count(self, obj):
        """Get published post count for category."""
        count = obj.posts.filter(status=Post.PUBLISHED).count()
        url = reverse('admin:templates_practice_post_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} posts</a>', url, count)
    post_count.short_description = 'Posts'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for Tag model."""
    list_display = ['name', 'slug', 'color_preview', 'post_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def color_preview(self, obj):
        """Show color preview."""
        return format_html(
            '<span style="background-color: {}; padding: 2px 8px; color: white; border-radius: 3px;">{}</span>',
            obj.color, obj.color
        )
    color_preview.short_description = 'Color'
    
    def post_count(self, obj):
        """Get published post count for tag."""
        count = obj.posts.filter(status=Post.PUBLISHED).count()
        return f'{count} posts'
    post_count.short_description = 'Posts'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin configuration for Author model."""
    list_display = ['full_name', 'user_email', 'post_count', 'website']
    list_filter = ['user__date_joined']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['user']
    
    def user_email(self, obj):
        """Get user email."""
        return obj.user.email
    user_email.short_description = 'Email'
    
    def post_count(self, obj):
        """Get published post count for author."""
        count = obj.posts.filter(status=Post.PUBLISHED).count()
        url = reverse('admin:templates_practice_post_changelist') + f'?author__id__exact={obj.id}'
        return format_html('<a href="{}">{} posts</a>', url, count)
    post_count.short_description = 'Posts'


class CommentInline(admin.TabularInline):
    """Inline for comments in post admin."""
    model = Comment
    fields = ['author_name', 'author_email', 'content', 'is_approved', 'is_spam']
    readonly_fields = ['author_name', 'author_email', 'content', 'created_at']
    extra = 0
    max_num = 5


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin configuration for Post model."""
    list_display = [
        'title', 'author', 'category', 'status', 'featured', 
        'view_count', 'published_at', 'reading_time'
    ]
    list_filter = [
        'status', 'featured', 'allow_comments', 'category', 
        'created_at', 'published_at'
    ]
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['view_count', 'created_at', 'updated_at', 'word_count']
    inlines = [CommentInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Content', {
            'fields': ('content', 'excerpt')
        }),
        ('Settings', {
            'fields': ('status', 'featured', 'allow_comments', 'tags')
        }),
        ('Publishing', {
            'fields': ('published_at',)
        }),
        ('Metadata', {
            'fields': ('view_count', 'reading_time', 'word_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['make_published', 'make_draft', 'make_featured']
    
    def make_published(self, request, queryset):
        """Mark posts as published."""
        updated = queryset.update(status=Post.PUBLISHED)
        self.message_user(request, f'{updated} posts marked as published.')
    make_published.short_description = 'Mark selected posts as published'
    
    def make_draft(self, request, queryset):
        """Mark posts as draft."""
        updated = queryset.update(status=Post.DRAFT)
        self.message_user(request, f'{updated} posts marked as draft.')
    make_draft.short_description = 'Mark selected posts as draft'
    
    def make_featured(self, request, queryset):
        """Mark posts as featured."""
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} posts marked as featured.')
    make_featured.short_description = 'Mark selected posts as featured'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for Comment model."""
    list_display = [
        'author_name', 'post', 'content_preview', 'is_approved', 
        'is_spam', 'is_reply', 'created_at'
    ]
    list_filter = ['is_approved', 'is_spam', 'created_at']
    search_fields = ['author_name', 'author_email', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['approve_comments', 'mark_as_spam', 'mark_as_not_spam']
    
    def content_preview(self, obj):
        """Show content preview."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def approve_comments(self, request, queryset):
        """Approve selected comments."""
        updated = queryset.update(is_approved=True, is_spam=False)
        self.message_user(request, f'{updated} comments approved.')
    approve_comments.short_description = 'Approve selected comments'
    
    def mark_as_spam(self, request, queryset):
        """Mark comments as spam."""
        updated = queryset.update(is_spam=True, is_approved=False)
        self.message_user(request, f'{updated} comments marked as spam.')
    mark_as_spam.short_description = 'Mark selected comments as spam'
    
    def mark_as_not_spam(self, request, queryset):
        """Mark comments as not spam."""
        updated = queryset.update(is_spam=False)
        self.message_user(request, f'{updated} comments marked as not spam.')
    mark_as_not_spam.short_description = 'Mark selected comments as not spam'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Admin configuration for Newsletter model."""
    list_display = ['email', 'name', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'name']
    readonly_fields = ['subscribed_at']
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        """Activate selected subscriptions."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscriptions activated.')
    activate_subscriptions.short_description = 'Activate selected subscriptions'
    
    def deactivate_subscriptions(self, request, queryset):
        """Deactivate selected subscriptions."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscriptions deactivated.')
    deactivate_subscriptions.short_description = 'Deactivate selected subscriptions'


@admin.register(TemplateExample)
class TemplateExampleAdmin(admin.ModelAdmin):
    """Admin configuration for TemplateExample model."""
    list_display = ['name', 'description_preview', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Template Code', {
            'fields': ('template_code',)
        }),
        ('Demo Data (JSON)', {
            'fields': ('demo_data',)
        }),
        ('Expected Output', {
            'fields': ('expected_output',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def description_preview(self, obj):
        """Show description preview."""
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_preview.short_description = 'Description'


# Customize admin site
admin.site.site_header = "Django Templates Practice Admin"
admin.site.site_title = "Templates Practice"
admin.site.index_title = "Welcome to Templates Practice Administration"
