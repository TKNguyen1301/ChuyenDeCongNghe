from django.urls import path, re_path, register_converter

from . import views
from . import converters

# Đăng ký custom converters
register_converter(converters.FourDigitYearConverter, 'yyyy')
register_converter(converters.MonthConverter, 'mm')
register_converter(converters.UsernameConverter, 'username')

# Ví dụ 1: Basic URL patterns với path converters
urlpatterns = [
    # Trường hợp đặc biệt phải đặt trước pattern tổng quát
    path("2003/", views.special_case_2003, name="special-2003"),
    
    # Sử dụng int converter để capture year
    path("<int:year>/", views.year_archive, name="news-year-archive"),
    
    # Capture cả year và month
    path("<int:year>/<int:month>/", views.month_archive, name="news-month-archive"),
    
    # Capture year, month và slug
    path("<int:year>/<int:month>/<slug:slug>/", views.article_detail, name="news-article-detail"),
    
    # URL đơn giản không có parameters
    path("", views.all_articles, name="articles-index"),
    
    # URL với string parameter mặc định
    path("latest/", views.latest_articles, name="latest-articles"),
    
    # URL cho redirect example
    path("redirect/", views.redirect_to_year, name="redirect-example"),
    
    # URL examples template
    path("examples/", views.url_examples, name="url-examples"),
    
    # Sử dụng custom converters
    path("custom/<yyyy:year>/", views.year_archive, name="custom-year-archive"),
    path("custom/<yyyy:year>/<mm:month>/", views.month_archive, name="custom-month-archive"),
]

# Ví dụ 2: Sử dụng regular expressions với re_path
re_patterns = [
    # Tương đương với pattern trên nhưng dùng regex
    re_path(r"^re/(?P<year>[0-9]{4})/$", views.year_archive, name="re-year-archive"),
    re_path(r"^re/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$", views.month_archive, name="re-month-archive"),
    re_path(r"^re/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<slug>[\w-]+)/$", views.article_detail, name="re-article-detail"),
]

# Thêm regex patterns vào urlpatterns
urlpatterns += re_patterns
