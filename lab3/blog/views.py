from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    """Blog index page"""
    return HttpResponse("Blog Index Page")


def archive(request):
    """Blog archive page"""
    return HttpResponse("Blog Archive Page")


def about(request):
    """Blog about page"""
    return HttpResponse("Blog About Page")


def page(request, num=1):
    """Blog page với default parameter"""
    return HttpResponse(f"Blog page number: {num}")


def post_detail(request, post_id):
    """Chi tiết bài viết blog"""
    return HttpResponse(f"Blog post detail: {post_id}")


def category_posts(request, category):
    """Bài viết theo danh mục"""
    return HttpResponse(f"Posts in category: {category}")


def tag_posts(request, tag):
    """Bài viết theo tag"""
    return HttpResponse(f"Posts with tag: {tag}")


def author_posts(request, username):
    """Bài viết theo tác giả"""
    return HttpResponse(f"Posts by author: {username}")
