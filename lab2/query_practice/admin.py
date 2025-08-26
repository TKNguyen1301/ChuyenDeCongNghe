"""
Admin configuration for Query Practice app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Blog, Author, Entry, EntryDetail, Category, Manufacturer, Product, Tag,
    Customer, Address, Order, OrderItem, Review, ProductView, SalesMetrics,
    Warehouse, Inventory, Promotion, WishList, WishListItem, ProductBundle, BundleItem
)


# ==================================================================
# Blog Models Admin
# ==================================================================

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['name', 'tagline']
    search_fields = ['name', 'tagline']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'birth_date']
    search_fields = ['name', 'email']
    list_filter = ['birth_date']


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ['headline', 'blog', 'pub_date', 'rating', 'number_of_comments']
    list_filter = ['blog', 'pub_date', 'rating']
    search_fields = ['headline', 'body_text']
    filter_horizontal = ['authors']
    date_hierarchy = 'pub_date'


@admin.register(EntryDetail)
class EntryDetailAdmin(admin.ModelAdmin):
    list_display = ['entry', 'created_at']
    search_fields = ['entry__headline', 'details']


# ==================================================================
# E-commerce Models Admin
# ==================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'description']
    list_filter = ['parent']
    search_fields = ['name', 'description']


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'founded_year', 'website']
    list_filter = ['country', 'founded_year']
    search_fields = ['name', 'country']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'manufacturer', 'price', 'stock_quantity', 'is_active', 'profit_margin_display']
    list_filter = ['category', 'manufacturer', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['tags']
    readonly_fields = ['created_at', 'updated_at']
    
    def profit_margin_display(self, obj):
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


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'color_display']
    search_fields = ['name']
    
    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; display: inline-block; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_display.short_description = 'Color Preview'


# ==================================================================
# Customer and Order Models Admin
# ==================================================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'loyalty_points', 'is_premium']
    list_filter = ['is_premium', 'date_of_birth']
    search_fields = ['user__username', 'user__email', 'phone']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'type', 'city', 'state', 'country', 'is_default']
    list_filter = ['type', 'city', 'state', 'country', 'is_default']
    search_fields = ['customer__user__username', 'street', 'city']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'order_date', 'total_amount', 'final_amount_display']
    list_filter = ['status', 'order_date']
    search_fields = ['order_number', 'customer__user__username']
    inlines = [OrderItemInline]
    readonly_fields = ['order_date']
    
    def final_amount_display(self, obj):
        return f"${obj.final_amount:,.2f}"
    final_amount_display.short_description = 'Final Amount'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'rating', 'title', 'is_verified_purchase', 'helpful_votes', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'customer__user__username', 'title', 'content']


# ==================================================================
# Analytics Models Admin
# ==================================================================

@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at', 'product']
    search_fields = ['product__name', 'customer__user__username', 'ip_address']
    readonly_fields = ['viewed_at']


@admin.register(SalesMetrics)
class SalesMetricsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_orders', 'total_revenue', 'total_items_sold', 'average_order_value', 'new_customers']
    list_filter = ['date']
    search_fields = ['date']


# ==================================================================
# Inventory Models Admin
# ==================================================================

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'manager', 'is_active']
    list_filter = ['is_active', 'manager']
    search_fields = ['name', 'code', 'address']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'reserved_quantity', 'available_quantity_display', 'last_updated']
    list_filter = ['warehouse', 'last_updated']
    search_fields = ['product__name', 'warehouse__name']
    readonly_fields = ['last_updated']
    
    def available_quantity_display(self, obj):
        available = obj.available_quantity
        if available <= 0:
            color = 'red'
        elif available < 10:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, available
        )
    available_quantity_display.short_description = 'Available'


# ==================================================================
# Promotion Models Admin
# ==================================================================

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'value', 'start_date', 'end_date', 'is_active', 'is_valid_display', 'current_uses']
    list_filter = ['type', 'is_active', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    filter_horizontal = ['products', 'categories']
    
    def is_valid_display(self, obj):
        if obj.is_valid:
            return format_html('<span style="color: green;">✓ Valid</span>')
        else:
            return format_html('<span style="color: red;">✗ Invalid</span>')
    is_valid_display.short_description = 'Status'


# ==================================================================
# Advanced Features Models Admin
# ==================================================================

class WishListItemInline(admin.TabularInline):
    model = WishListItem
    extra = 1


@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ['customer', 'name', 'is_public', 'created_at', 'items_count']
    list_filter = ['is_public', 'created_at']
    search_fields = ['customer__user__username', 'name']
    inlines = [WishListItemInline]
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Items Count'


class BundleItemInline(admin.TabularInline):
    model = BundleItem
    extra = 1


@admin.register(ProductBundle)
class ProductBundleAdmin(admin.ModelAdmin):
    list_display = ['name', 'bundle_price', 'is_active', 'created_at', 'savings_display']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    inlines = [BundleItemInline]
    
    def savings_display(self, obj):
        savings = obj.savings
        if savings > 0:
            return format_html(
                '<span style="color: green;">${:.2f}</span>',
                savings
            )
        else:
            return format_html(
                '<span style="color: red;">${:.2f}</span>',
                savings
            )
    savings_display.short_description = 'Savings'
