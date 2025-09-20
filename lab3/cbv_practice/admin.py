from django.contrib import admin
from .models import Author, Category, Book, Article, Comment


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'birth_date', 'created_at']
    list_filter = ['created_at', 'birth_date']
    search_fields = ['name', 'email']
    readonly_fields = ['created_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'publication_date', 'price', 'is_available']
    list_filter = ['category', 'is_available', 'publication_date', 'created_at']
    search_fields = ['title', 'description', 'isbn']
    filter_horizontal = ['authors']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'publication_date'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'published_date', 'views_count']
    list_filter = ['category', 'is_published', 'published_date']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count']
    date_hierarchy = 'published_date'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['article', 'author_name', 'author_email', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['author_name', 'author_email', 'content']
    readonly_fields = ['created_at']
