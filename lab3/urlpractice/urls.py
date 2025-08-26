"""
URL configuration for urlpractice project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# Simple view cho trang chủ
def home(request):
    return HttpResponse("""
    <h1>Django Practice Lab 3</h1>
    <h2>Available Sections:</h2>
    <ul>
        <li><a href="/articles/">📰 Articles App (URL Dispatcher Practice)</a></li>
        <li><a href="/blog/">📝 Blog App (Namespaces Practice)</a></li>
        <li><a href="/views/">👁️ Views Practice (Django Views)</a></li>
        <li><a href="/author-blog/">✍️ Author Blog (Namespace Instance)</a></li>
        <li><a href="/publisher-blog/">📚 Publisher Blog (Namespace Instance)</a></li>
        <li><a href="/admin/">⚙️ Admin</a></li>
    </ul>
    
    <h3>📰 Articles Examples (URL Practice):</h3>
    <ul>
        <li><a href="/articles/2003/">Special case 2003</a></li>
        <li><a href="/articles/2024/">Year archive 2024</a></li>
        <li><a href="/articles/2024/12/">Month archive 2024/12</a></li>
        <li><a href="/articles/2024/12/django-urls/">Article detail</a></li>
        <li><a href="/articles/custom/2024/">Custom converter example</a></li>
        <li><a href="/articles/examples/">URL Examples Template</a></li>
    </ul>
    
    <h3>👁️ Views Examples:</h3>
    <ul>
        <li><a href="/views/current-datetime/">Simple View - Current DateTime</a></li>
        <li><a href="/views/hello/">Hello World View</a></li>
        <li><a href="/views/params/Django/25/">View with Parameters</a></li>
        <li><a href="/views/item/999/">404 Exception Demo</a></li>
        <li><a href="/views/json/">JSON Response</a></li>
        <li><a href="/views/async-datetime/">Async View</a></li>
        <li><a href="/views/form/">Form Handling</a></li>
    </ul>
    
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2, h3 { color: #34495e; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 8px 0; padding: 10px; background: #f8f9fa; border-left: 4px solid #3498db; }
        a { color: #2980b9; text-decoration: none; font-weight: bold; }
        a:hover { color: #3498db; }
    </style>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    
    # Include articles app URLs
    path('articles/', include('articles.urls')),
    
    # Include blog app URLs với application namespace
    path('blog/', include('blog.urls')),
    
    # Include views practice URLs
    path('views/', include('views_practice.urls')),
    
    # Multiple instances với different instance namespaces
    path('author-blog/', include('blog.urls', namespace='author-blog')),
    path('publisher-blog/', include('blog.urls', namespace='publisher-blog')),
    
    # Ví dụ về extra options
    path('special-blog/', include('blog.urls'), {'special': True}),
]

# Custom error handlers (theo tài liệu Django)
handler404 = 'views_practice.views.custom_404_view'
handler500 = 'views_practice.views.custom_500_view'
handler403 = 'views_practice.views.custom_403_view'
handler400 = 'django.views.defaults.bad_request'
