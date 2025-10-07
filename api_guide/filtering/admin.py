from django.contrib import admin
from .models import Category, Product, Purchase, UserProfile, Review, Booking


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'in_stock', 'stock_quantity', 'owner', 'created_at']
    list_filter = ['category', 'in_stock', 'created_at', 'owner']
    search_fields = ['name', 'description', 'owner__username']
    date_hierarchy = 'created_at'
    raw_id_fields = ['owner']
    list_editable = ['price', 'in_stock', 'stock_quantity']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['purchaser', 'product', 'quantity', 'total_price', 'status', 'purchase_date']
    list_filter = ['status', 'purchase_date', 'product__category']
    search_fields = ['purchaser__username', 'product__name', 'notes']
    date_hierarchy = 'purchase_date'
    raw_id_fields = ['purchaser', 'product']
    list_editable = ['status']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profession', 'location', 'birth_date']
    search_fields = ['user__username', 'profession', 'location', 'bio']
    list_filter = ['profession', 'location']
    raw_id_fields = ['user']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['title', 'product', 'reviewer', 'rating', 'verified_purchase', 'created_at']
    list_filter = ['rating', 'verified_purchase', 'created_at', 'product__category']
    search_fields = ['title', 'content', 'reviewer__username', 'product__name']
    date_hierarchy = 'created_at'
    raw_id_fields = ['product', 'reviewer']
    list_editable = ['verified_purchase']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'priority', 'start_date', 'end_date', 'created_at']
    list_filter = ['status', 'priority', 'start_date', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user']
    list_editable = ['status', 'priority']