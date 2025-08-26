"""
Admin configuration for Model Class Practice app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Article, Book, Event, Product, Profile, Order, 
    Analytics, SimpleNote, BlogPost
)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'published_date', 'view_count', 'created']
    list_filter = ['status', 'created', 'published_date']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'created', 'updated']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'content')
        }),
        ('Publishing', {
            'fields': ('status', 'published_date', 'is_published')
        }),
        ('Meta', {
            'fields': ('view_count', 'created', 'updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'publication_date', 'price', 'available']
    list_filter = ['available', 'publication_date']
    search_fields = ['title', 'author', 'isbn']
    ordering = ['title']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_date', 'location', 'max_attendees', 'is_active']
    list_filter = ['is_active', 'event_date']
    search_fields = ['name', 'location']
    date_hierarchy = 'event_date'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'cost', 'profit_margin_display', 'stock_quantity', 'is_low_stock_display', 'is_active']
    list_filter = ['is_active', 'created']
    search_fields = ['name', 'sku']
    readonly_fields = ['created', 'updated', 'profit_margin_display']
    
    def profit_margin_display(self, obj):
        """Display profit margin with color coding."""
        margin = obj.profit_margin
        if margin > 50:
            color = 'green'
        elif margin > 20:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, margin
        )
    profit_margin_display.short_description = 'Profit Margin'
    
    def is_low_stock_display(self, obj):
        """Display low stock indicator."""
        if obj.is_low_stock():
            return format_html('<span style="color: red;">⚠️ Low Stock</span>')
        return format_html('<span style="color: green;">✅ In Stock</span>')
    is_low_stock_display.short_description = 'Stock Status'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'uuid', 'is_verified', 'website']
    list_filter = ['is_verified']
    search_fields = ['user__username', 'bio']
    readonly_fields = ['uuid']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'created']
    list_filter = ['status', 'created']
    search_fields = ['order_number', 'user__username']
    readonly_fields = ['order_number', 'created', 'updated']
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly if order is not editable."""
        readonly = list(self.readonly_fields)
        if obj and not obj.is_editable():
            readonly.extend(['user', 'total_amount'])
        return readonly


@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ['article', 'date', 'page_views', 'unique_visitors', 'bounce_rate', 'computed_score']
    list_filter = ['date']
    search_fields = ['article__title']
    readonly_fields = ['computed_score']
    date_hierarchy = 'date'


@admin.register(SimpleNote)
class SimpleNoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'get_priority_display', 'created']
    list_filter = ['priority', 'created']
    search_fields = ['title', 'content']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created', 'updated', 'age_in_days']
    list_filter = ['created', 'author']
    search_fields = ['title', 'content']
    readonly_fields = ['created', 'updated']
    
    def age_in_days(self, obj):
        """Display age in days."""
        return f"{obj.age_in_days()} days"
    age_in_days.short_description = 'Age'
