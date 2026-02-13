from django.contrib import admin
from .models import (
    Product, Order, OrderItem, Article, Comment, 
    Billing, Account
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'price', 'stock_quantity', 'created']
    list_filter = ['category', 'created']
    search_fields = ['name', 'description', 'category']
    ordering = ['-created']
    readonly_fields = ['created', 'updated']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['created']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'total_amount', 'order_date']
    list_filter = ['status', 'order_date']
    search_fields = ['customer__username', 'shipping_address']
    ordering = ['-order_date']
    readonly_fields = ['order_date', 'created']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'unit_price']
    list_filter = ['created']
    search_fields = ['product__name', 'order__id']
    ordering = ['-created']
    readonly_fields = ['created']


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['created']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'published', 'view_count', 'created']
    list_filter = ['published', 'created', 'author']
    search_fields = ['title', 'content', 'author__username']
    ordering = ['-created']
    readonly_fields = ['created', 'updated']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'article', 'author', 'created']
    list_filter = ['created']
    search_fields = ['content', 'author__username', 'article__title']
    ordering = ['-created']
    readonly_fields = ['created']


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'amount', 'billing_date', 'paid']
    list_filter = ['paid', 'billing_date']
    search_fields = ['customer__username', 'description']
    ordering = ['-billing_date']
    readonly_fields = ['created']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'account_number', 'user', 'account_type', 'balance', 'is_active']
    list_filter = ['account_type', 'is_active', 'created']
    search_fields = ['account_number', 'user__username', 'user__email']
    ordering = ['-created']
    readonly_fields = ['created']