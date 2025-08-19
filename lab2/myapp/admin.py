from django.contrib import admin
from .models import (Person, Student, StudentInherited, Manufacturer, Car, 
                    Topping, Pizza, Group, Membership, Place, Restaurant, 
                    Waiter, Blog, Product, ServerLog, Document, Order, OrderItem, 
                    UserProfile, Article, BlogPost, AdvancedIndexDemo, 
                    SearchableContent, FullTextSearchDemo, UniqueIndexDemo, 
                    PerformanceOptimizedModel)

# Register your models here.

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'birth_date', 'age', 'baby_boomer_status']
    search_fields = ['first_name', 'last_name']
    list_filter = ['birth_date']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'year_in_school', 'is_active', 'gpa']
    list_filter = ['year_in_school', 'is_active']
    search_fields = ['name', 'email']


@admin.register(StudentInherited)
class StudentInheritedAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'home_group']
    search_fields = ['name']


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'founded_date']
    search_fields = ['name', 'country']
    list_filter = ['country']


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'year', 'price', 'is_electric', 'is_vintage']
    list_filter = ['manufacturer', 'year', 'is_electric']
    search_fields = ['name']


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'address']
    search_fields = ['name', 'address']


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'serves_hot_dogs', 'serves_pizza']
    list_filter = ['serves_hot_dogs', 'serves_pizza']


@admin.register(Waiter)
class WaiterAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant']
    list_filter = ['restaurant']


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['name', 'tagline', 'created_at']
    search_fields = ['name', 'tagline']


@admin.register(Topping)
class ToppingAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    filter_horizontal = ['toppings']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['person', 'group', 'date_joined', 'invite_reason']
    list_filter = ['date_joined']


# ============ ADMIN CHO CÁC MODELS MỚI ============

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'quantity', 'is_active', 'is_featured', 'created_at']
    list_filter = ['is_active', 'is_featured', 'created_at', 'category_priority']
    search_fields = ['name', 'slug', 'description']
    list_editable = ['price', 'quantity', 'is_active', 'is_featured']
    readonly_fields = ['id', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ServerLog)
class ServerLogAdmin(admin.ModelAdmin):
    list_display = ['log_id', 'client_ip', 'server_ip', 'status_code', 'timestamp', 'daily_sequence']
    list_filter = ['status_code', 'timestamp', 'log_date']
    search_fields = ['client_ip', 'server_ip', 'message']
    readonly_fields = ['log_id', 'timestamp', 'log_date']
    ordering = ['-timestamp']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'file', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['title']
    readonly_fields = ['uploaded_at', 'thumbnail_height', 'thumbnail_width']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'priority', 'total_amount', 'order_date']
    list_filter = ['status', 'priority', 'order_date']
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name']
    readonly_fields = ['order_date']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price']
    list_filter = ['order__status']
    search_fields = ['order__order_number', 'product__name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'country', 'date_of_birth', 'date_joined']
    list_filter = ['country', 'date_joined']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['date_joined']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'published_date', 'created_at']
    list_filter = ['published_date', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['authors']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BlogPost)
class NewBlogPostAdmin(admin.ModelAdmin):  # Đổi tên class để tránh xung đột
    list_display = ['title', 'author', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at', 'author']
    search_fields = ['title', 'content']
    list_editable = ['is_published']


# ============ ADMIN CHO CÁC INDEX DEMO MODELS ============

# Tạm thời comment admin classes có lỗi
# @admin.register(AdvancedIndexDemo)  
# @admin.register(PerformanceOptimizedModel)
    readonly_fields = ['created_at', 'updated_at']
