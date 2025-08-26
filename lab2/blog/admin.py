from django.contrib import admin
from .models import (
    Person, Musician, Album, Student, Topping, Pizza,
    AdvancedFieldExample, Product, Author, Book, Review
)

# Đăng ký các models để quản lý trong admin
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name']
    search_fields = ['first_name', 'last_name']

@admin.register(Musician)
class MusicianAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'instrument']
    search_fields = ['first_name', 'last_name', 'instrument']

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'artist', 'release_date', 'num_stars']
    list_filter = ['release_date', 'num_stars']
    search_fields = ['name', 'artist__first_name', 'artist__last_name']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'year_in_school', 'is_upperclass']
    list_filter = ['year_in_school']
    search_fields = ['name']

@admin.register(Topping)
class ToppingAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ['toppings']  # Hiển thị toppings dạng horizontal filter
    search_fields = ['name']

@admin.register(AdvancedFieldExample)
class AdvancedFieldExampleAdmin(admin.ModelAdmin):
    list_display = ['title', 'email', 'is_active', 'priority', 'score', 'datetime_field']
    list_filter = ['is_active', 'priority', 'date_field']
    search_fields = ['title', 'description', 'email']
    readonly_fields = ['id', 'date_field', 'datetime_field']
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'slug')
        }),
        ('Contact', {
            'fields': ('email', 'website')
        }),
        ('Numbers', {
            'fields': ('integer_field', 'float_field', 'decimal_field', 'score'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'priority')
        }),
        ('Dates & Times', {
            'fields': ('date_field', 'datetime_field', 'time_field', 'duration_field'),
            'classes': ('collapse',)
        }),
        ('Technical', {
            'fields': ('ip_address', 'json_data', 'binary_data'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'is_available', 'created_date']
    list_filter = ['is_available', 'created_date']
    search_fields = ['name', 'sku']
    readonly_fields = ['created_date']

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'birth_date']
    search_fields = ['name', 'email']

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'isbn', 'publication_date', 'pages', 'price', 'is_published']
    list_filter = ['is_published', 'publication_date']
    search_fields = ['title', 'isbn']
    filter_horizontal = ['authors']
    inlines = [ReviewInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['book', 'reviewer_name', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['book__title', 'reviewer_name']
