"""
Django Admin Configuration for Meta Practice Models
Demonstrates how Meta options affect admin interface
"""

from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.utils.html import format_html

from .models import (
    BlogPost, Category, Tag, Question, Answer, 
    PublishedBlogPost, Product, ConfigurableModel,
    CompleteExampleModel, LegacyModel
)


# ==================================================================
# 1. BlogPost Admin - Custom Table Name and Permissions
# ==================================================================

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published', 'views_count', 'created']
    list_filter = ['published', 'created', 'author']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created', 'modified', 'views_count']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'author')
        }),
        ('Status', {
            'fields': ('published',)
        }),
        ('Metadata', {
            'fields': ('views_count', 'created', 'modified'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        # Utilize the ordering defined in Meta
        return super().get_queryset(request)
    
    def has_publish_permission(self, request):
        """Check custom permission defined in Meta."""
        return request.user.has_perm('meta_practice.can_publish_post')


# ==================================================================
# 2. Category Admin - Ordering and Hierarchical Structure
# ==================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order', 'subcategory_count']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']  # Uses Meta ordering
    
    def subcategory_count(self, obj):
        """Show number of subcategories."""
        return obj.subcategories.count()
    subcategory_count.short_description = 'Subcategories'
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            subcategory_count=Count('subcategories')
        )


# ==================================================================
# 3. Tag Admin - Custom Permissions and Ordering
# ==================================================================

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'colored_name', 'usage_count']
    list_filter = ['usage_count']
    search_fields = ['name']
    ordering = ['-usage_count', 'name']  # Uses Meta ordering
    readonly_fields = ['usage_count']
    
    def colored_name(self, obj):
        """Display tag name with its color."""
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            obj.color,
            obj.name
        )
    colored_name.short_description = 'Colored Name'
    
    def has_delete_permission(self, request, obj=None):
        """No delete permission as defined in Meta default_permissions."""
        return False


# ==================================================================
# 4. Question and Answer Admin - Order with Respect To
# ==================================================================

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text_preview', 'category', 'author', 'created', 'answer_count']
    list_filter = ['category', 'created', 'author']
    search_fields = ['text']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Question'
    
    def answer_count(self, obj):
        return obj.answer_set.count()
    answer_count.short_description = 'Answers'


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    fields = ['text', 'author', 'is_correct', 'votes']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'author', 'is_correct', 'votes', 'created']
    list_filter = ['is_correct', 'created', 'author']
    search_fields = ['text', 'question__text']
    
    def question_preview(self, obj):
        return obj.question.text[:30] + '...'
    question_preview.short_description = 'Question'
    
    # Note: order_with_respect_to creates special ordering methods
    # You can use obj.get_next_in_order() and obj.get_previous_in_order()


# ==================================================================
# 5. Proxy Model Admin - PublishedBlogPost
# ==================================================================

@admin.register(PublishedBlogPost)
class PublishedBlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'views_count', 'analytics_preview', 'created']
    list_filter = ['created', 'author']
    search_fields = ['title', 'content']
    ordering = ['-views_count', '-created']  # Uses proxy Meta ordering
    
    def get_queryset(self, request):
        # Only show published posts
        return super().get_queryset(request).filter(published=True)
    
    def analytics_preview(self, obj):
        """Show analytics data from proxy model method."""
        data = obj.get_analytics_data()
        return f"Views: {data['views']}, Days: {data['days_since_published']}"
    analytics_preview.short_description = 'Analytics'
    
    def has_view_analytics_permission(self, request):
        """Check proxy model custom permission."""
        return request.user.has_perm('meta_practice.can_view_analytics')


# ==================================================================
# 6. Product Admin - Complex Meta Options
# ==================================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'category', 'is_active', 'stock_quantity']
    list_filter = ['category', 'is_active', 'created']
    search_fields = ['name', 'sku']
    filter_horizontal = ['tags']
    readonly_fields = ['created', 'updated']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'category')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock_quantity', 'is_active')
        }),
        ('Categorization', {
            'fields': ('tags',)
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        # Uses Meta ordering: ['category__name', 'name']
        return super().get_queryset(request).select_related('category')
    
    def has_manage_inventory_permission(self, request):
        """Check custom permission."""
        return request.user.has_perm('meta_practice.can_manage_inventory')


# ==================================================================
# 7. ConfigurableModel Admin - Custom Managers
# ==================================================================

@admin.register(ConfigurableModel)
class ConfigurableModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'priority', 'is_active']
    list_filter = ['is_active', 'priority']
    search_fields = ['name']
    ordering = ['-priority', 'name']  # Uses Meta ordering
    
    def get_queryset(self, request):
        # You can choose which manager to use
        # Uses default_manager_name from Meta
        return ConfigurableModel.objects.all()
        # Or use custom manager: return ConfigurableModel.custom.all()


# ==================================================================
# 8. CompleteExampleModel Admin - All Meta Options
# ==================================================================

@admin.register(CompleteExampleModel)
class CompleteExampleModelAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'priority', 'is_featured', 
        'is_active', 'view_count', 'created'
    ]
    list_filter = ['category', 'is_featured', 'is_active', 'priority']
    search_fields = ['title', 'description']
    filter_horizontal = ['tags']
    readonly_fields = ['created', 'modified', 'view_count']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'description', 'category', 'tags')
        }),
        ('Status & Priority', {
            'fields': ('priority', 'is_featured', 'is_active')
        }),
        ('Analytics', {
            'fields': ('view_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        # Uses Meta ordering: ['-is_featured', '-priority', '-created']
        return super().get_queryset(request).select_related('category')
    
    def has_feature_permission(self, request):
        """Check custom permission."""
        return request.user.has_perm('meta_practice.can_feature')


# ==================================================================
# 9. LegacyModel Admin - Legacy Meta Options
# ==================================================================

@admin.register(LegacyModel)
class LegacyModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone']
    search_fields = ['name', 'email']
    
    def get_queryset(self, request):
        # Shows how unique_together works in practice
        return super().get_queryset(request)


# ==================================================================
# Custom Admin Views for Meta Options Demonstration
# ==================================================================

class MetaOptionsInspector:
    """Helper class to inspect Meta options."""
    
    @staticmethod
    def get_meta_info(model_class):
        """Get comprehensive Meta options information."""
        meta = model_class._meta
        return {
            'model_name': meta.model_name,
            'verbose_name': meta.verbose_name,
            'verbose_name_plural': meta.verbose_name_plural,
            'db_table': meta.db_table,
            'ordering': meta.ordering,
            'get_latest_by': meta.get_latest_by,
            'permissions': getattr(meta, 'permissions', []),
            'default_permissions': meta.default_permissions,
            'abstract': meta.abstract,
            'proxy': meta.proxy,
            'managed': meta.managed,
        }


# Register models that demonstrate database-specific features
# Note: These won't appear in admin if database requirements aren't met
try:
    from .models import PostgreSQLSpecificModel, GISEnabledModel
    
    # Only register if database supports it
    admin.site.register(PostgreSQLSpecificModel)
    admin.site.register(GISEnabledModel)
except Exception:
    # Models won't be created if database requirements aren't met
    pass


# Customize admin site headers to show Meta options demonstration
admin.site.site_header = "Django Meta Options Administration"
admin.site.site_title = "Meta Options Demo"
admin.site.index_title = "Explore Django Model Meta Options"
