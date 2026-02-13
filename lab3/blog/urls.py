from django.urls import path, include

from . import views

# Đặt app_name để tạo application namespace
app_name = 'blog'

urlpatterns = [
    # Basic patterns
    path("", views.index, name="index"),
    path("archive/", views.archive, name="archive"),
    path("about/", views.about, name="about"),
    
    # Pattern với default parameter
    path("page/", views.page, name="page-default"),
    path("page/<int:num>/", views.page, name="page"),
    
    # Chi tiết bài viết
    path("post/<int:post_id>/", views.post_detail, name="post-detail"),
    
    # Danh mục và tag
    path("category/<str:category>/", views.category_posts, name="category"),
    path("tag/<slug:tag>/", views.tag_posts, name="tag"),
    
    # Tác giả
    path("author/<str:username>/", views.author_posts, name="author"),
]

# Ví dụ về nested patterns để tránh lặp lại
nested_patterns = [
    path("history/", views.archive, name="history"),
    path("edit/", views.about, name="edit"),
    path("discuss/", views.index, name="discuss"),
    path("permissions/", views.index, name="permissions"),
]

# Thêm nested patterns với prefix chung
urlpatterns += [
    path("post/<int:post_id>/", include(nested_patterns)),
]
