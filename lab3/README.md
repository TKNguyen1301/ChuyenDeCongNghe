# Lab 3: Django URL Dispatcher Practice

Đây là lab thực hành về Django URL dispatcher dựa trên tài liệu chính thức tại: https://docs.djangoproject.com/en/5.2/topics/http/urls/

## Cấu trúc Project

```
lab3/
├── urlpractice/          # Main Django project
│   ├── settings.py
│   ├── urls.py          # Root URLconf
│   └── ...
├── articles/            # App thực hành URL patterns
│   ├── views.py         # Views demo các tính năng
│   ├── urls.py          # URLconf với path converters
│   └── converters.py    # Custom path converters
├── blog/               # App thực hành namespaces
│   ├── views.py        # Views demo blog
│   └── urls.py         # URLconf với namespaces
├── templates/          # Templates demo reverse URLs
│   └── url_examples.html
└── README.md           # File này
```

## Các Tính Năng Được Demo

### 1. Basic URL Patterns
- Path converters: `str`, `int`, `slug`, `uuid`, `path`
- URL pattern ordering (đặt pattern cụ thể trước pattern tổng quát)
- Default parameters cho views

### 2. Custom Path Converters
- `FourDigitYearConverter`: Chỉ accept năm 4 chữ số
- `MonthConverter`: Chỉ accept tháng 01-12
- `UsernameConverter`: Chỉ accept chữ, số và underscore

### 3. Regular Expressions
- Sử dụng `re_path()` thay vì `path()`
- Named groups: `(?P<name>pattern)`
- So sánh với path converters

### 4. Including URLconfs
- Sử dụng `include()` để chia nhỏ URLs
- Nested patterns để tránh lặp lại

### 5. URL Namespaces
- Application namespace với `app_name`
- Instance namespace với `namespace` parameter
- Multiple instances của cùng một app

### 6. Reverse URL Resolution
- Trong Python code: `reverse()`
- Trong templates: `{% url %}`
- Với namespaces: `blog:index`

### 7. Extra Options
- Passing extra parameters to views
- Passing extra options to `include()`

## Cách Chạy Project

1. Activate virtual environment:
```bash
source /path/to/venv/bin/activate
```

2. Navigate to lab3 directory:
```bash
cd lab3
```

3. Run development server:
```bash
python manage.py runserver
```

4. Truy cập các URL để test:

### URL Examples

#### Articles App:
- `/articles/` - All articles
- `/articles/2003/` - Special case for 2003
- `/articles/2024/` - Year archive
- `/articles/2024/12/` - Month archive
- `/articles/2024/12/django-urls/` - Article detail
- `/articles/custom/2024/` - Custom converter example
- `/articles/examples/` - Template với reverse URLs

#### Blog App (với namespaces):
- `/blog/` - Blog index
- `/blog/page/5/` - Blog page 5
- `/author-blog/` - Author blog instance
- `/publisher-blog/` - Publisher blog instance

#### Regex Examples:
- `/articles/re/2024/` - Year với regex
- `/articles/re/2024/12/` - Month với regex

## Các Pattern Quan Trọng

### 1. URL Pattern Order
```python
urlpatterns = [
    path("2003/", views.special_case_2003),  # Cụ thể trước
    path("<int:year>/", views.year_archive),  # Tổng quát sau
]
```

### 2. Path Converters
```python
path("<int:year>/", views.year_archive)           # int converter
path("<slug:slug>/", views.article_detail)        # slug converter
path("<str:category>/", views.category_posts)     # str converter (default)
```

### 3. Custom Converters
```python
register_converter(converters.FourDigitYearConverter, 'yyyy')
path("<yyyy:year>/", views.year_archive)
```

### 4. Namespaces
```python
# app/urls.py
app_name = 'blog'
urlpatterns = [...]

# main/urls.py
path('blog/', include('blog.urls')),
path('author-blog/', include('blog.urls', namespace='author-blog')),
```

### 5. Reverse URLs
```python
# Trong Python
reverse('blog:index')
reverse('news-year-archive', args=(2024,))

# Trong templates
{% url 'blog:index' %}
{% url 'news-year-archive' 2024 %}
```

## Bài Tập Thực Hành

1. Thêm các URL patterns mới
2. Tạo custom converter cho email
3. Thực hành nested namespaces
4. Tạo error handlers custom
5. Sử dụng extra options trong views

## Tài Liệu Tham Khảo

- [Django URL Dispatcher](https://docs.djangoproject.com/en/5.2/topics/http/urls/)
- [URL reversing](https://docs.djangoproject.com/en/5.2/ref/urlresolvers/)
- [Built-in path converters](https://docs.djangoproject.com/en/5.2/topics/http/urls/#path-converters)
