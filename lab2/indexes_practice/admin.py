from django.contrib import admin
from .models import Article, Product, Customer, Order, LogEntry

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'category', 'view_count', 'rating', 'is_featured', 'created_at']
    list_filter = ['status', 'category', 'is_featured', 'is_premium', 'created_at']
    search_fields = ['title', 'slug', 'content', 'tags']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'summary', 'tags')
        }),
        ('Metadata', {
            'fields': ('status', 'category', 'is_featured', 'is_premium')
        }),
        ('Analytics', {
            'fields': ('view_count', 'rating', 'word_count'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'brand', 'price', 'stock_quantity', 'is_active', 'sales_count']
    list_filter = ['is_active', 'is_digital', 'category', 'brand', 'created_at']
    search_fields = ['name', 'sku', 'barcode', 'category', 'brand']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'sku', 'barcode')
        }),
        ('Categorization', {
            'fields': ('category', 'subcategory', 'brand')
        }),
        ('Pricing', {
            'fields': ('price', 'cost', 'discount_percentage')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'is_active', 'is_digital')
        }),
        ('Analytics', {
            'fields': ('sales_count', 'views_count'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'launch_date'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'customer_tier', 'is_vip', 'total_orders', 'total_spent', 'date_joined']
    list_filter = ['is_active', 'is_vip', 'customer_tier', 'country', 'date_joined']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['date_joined']
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'
    
    fieldsets = (
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Location', {
            'fields': ('city', 'country', 'postal_code')
        }),
        ('Status', {
            'fields': ('is_active', 'is_vip', 'customer_tier')
        }),
        ('Analytics', {
            'fields': ('total_orders', 'total_spent', 'lifetime_value'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_joined', 'last_login', 'last_purchase'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_email', 'status', 'total_amount', 'items_count', 'created_at']
    list_filter = ['status', 'shipping_method', 'created_at']
    search_fields = ['order_number', 'customer__email', 'customer__first_name', 'customer__last_name', 'tracking_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def customer_email(self, obj):
        return obj.customer.email
    customer_email.short_description = 'Customer Email'
    
    fieldsets = (
        ('Order Info', {
            'fields': ('id', 'order_number', 'customer', 'status')
        }),
        ('Financial', {
            'fields': ('subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount')
        }),
        ('Shipping', {
            'fields': ('shipping_method', 'tracking_number'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('items_count',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'level', 'module', 'function', 'user_id', 'duration_ms', 'message_preview']
    list_filter = ['level', 'module', 'timestamp']
    search_fields = ['message', 'module', 'function', 'request_path']
    readonly_fields = ['timestamp']
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message Preview'
    
    fieldsets = (
        ('Log Info', {
            'fields': ('level', 'message', 'module', 'function')
        }),
        ('Context', {
            'fields': ('user_id', 'ip_address', 'request_path'),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('timestamp', 'duration_ms'),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('user_agent', 'extra_data'),
            'classes': ('collapse',)
        }),
    )
