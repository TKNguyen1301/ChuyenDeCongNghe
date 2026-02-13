from django.http import HttpResponse, HttpResponseNotFound, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods
import datetime
import json


# ========== Simple Views (theo tài liệu) ==========

def current_datetime(request):
    """
    Simple view trả về thời gian hiện tại - Ví dụ từ tài liệu Django
    """
    now = datetime.datetime.now()
    html = '<html lang="en"><body>It is now %s.</body></html>' % now
    return HttpResponse(html)


def simple_hello(request):
    """View đơn giản trả về Hello World"""
    return HttpResponse("<h1>Hello, World!</h1>")


def view_with_parameters(request, name, age):
    """View với parameters từ URL"""
    html = f"""
    <html>
    <head><title>User Info</title></head>
    <body>
        <h1>User Information</h1>
        <p>Name: {name}</p>
        <p>Age: {age}</p>
    </body>
    </html>
    """
    return HttpResponse(html)


# ========== Error Handling Views ==========

def view_with_404_exception(request, item_id):
    """
    View demo Http404 exception
    """
    # Giả lập data
    items = {1: "Item 1", 2: "Item 2", 3: "Item 3"}
    
    if item_id not in items:
        raise Http404("Item does not exist")
    
    html = f"""
    <html>
    <body>
        <h1>Item Details</h1>
        <p>ID: {item_id}</p>
        <p>Name: {items[item_id]}</p>
    </body>
    </html>
    """
    return HttpResponse(html)


def view_with_custom_404(request):
    """View trả về HttpResponseNotFound tùy chỉnh"""
    return HttpResponseNotFound("<h1>Custom 404 - Page not found</h1>")


def view_with_custom_status(request):
    """View trả về HTTP status code tùy chỉnh"""
    return HttpResponse("Resource created successfully", status=201)


def view_with_permission_denied(request):
    """View demo PermissionDenied exception"""
    # Kiểm tra quyền truy cập giả lập
    user_has_permission = False  # Giả lập user không có quyền
    
    if not user_has_permission:
        raise PermissionDenied("You don't have permission to access this resource")
    
    return HttpResponse("Secret content")


# ========== Views với HTTP Methods ==========

@require_http_methods(["GET", "POST"])
def method_specific_view(request):
    """View chỉ accept GET và POST"""
    if request.method == "GET":
        return HttpResponse("This is a GET request")
    elif request.method == "POST":
        return HttpResponse("This is a POST request")


def all_methods_view(request):
    """View hiển thị thông tin về HTTP method"""
    method = request.method
    html = f"""
    <html>
    <body>
        <h1>HTTP Method: {method}</h1>
        <p>Request path: {request.path}</p>
        <p>Query string: {request.GET}</p>
        <p>User agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}</p>
    </body>
    </html>
    """
    return HttpResponse(html)


# ========== Async Views ==========

async def async_current_datetime(request):
    """
    Async view trả về thời gian hiện tại - Ví dụ từ tài liệu Django
    """
    import asyncio
    await asyncio.sleep(0.1)  # Simulate async operation
    
    now = datetime.datetime.now()
    html = '<html lang="en"><body>Async view - It is now %s.</body></html>' % now
    return HttpResponse(html)


# ========== JSON Response Views ==========

def json_response_view(request):
    """View trả về JSON response"""
    data = {
        'message': 'Hello from Django!',
        'timestamp': datetime.datetime.now().isoformat(),
        'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
        'method': request.method,
        'path': request.path
    }
    return JsonResponse(data)


def json_response_with_params(request, user_id):
    """View trả về JSON với parameters"""
    # Giả lập user data
    users = {
        1: {'name': 'John Doe', 'email': 'john@example.com'},
        2: {'name': 'Jane Smith', 'email': 'jane@example.com'},
        3: {'name': 'Bob Johnson', 'email': 'bob@example.com'},
    }
    
    if user_id not in users:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    user_data = users[user_id]
    user_data['id'] = user_id
    return JsonResponse(user_data)


# ========== Template-based Views ==========

def template_view(request):
    """View sử dụng template"""
    context = {
        'title': 'Views Practice',
        'current_time': datetime.datetime.now(),
        'request_info': {
            'method': request.method,
            'path': request.path,
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown')
        }
    }
    return render(request, 'views_practice/template_example.html', context)


def template_with_params(request, category, item_id):
    """View sử dụng template với parameters"""
    context = {
        'category': category,
        'item_id': item_id,
        'title': f'Item {item_id} in {category}',
        'breadcrumb': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Views Practice', 'url': '/views/'},
            {'name': category.title(), 'url': f'/views/category/{category}/'},
            {'name': f'Item {item_id}', 'url': ''}
        ]
    }
    return render(request, 'views_practice/item_detail.html', context)


# ========== Redirect Views ==========

from django.shortcuts import redirect
from django.urls import reverse

def redirect_view(request):
    """View redirect đến view khác"""
    return redirect('views_practice:current_datetime')


def redirect_with_params(request):
    """View redirect với parameters"""
    return redirect('views_practice:view_params', name='Django', age=18)


def redirect_external(request):
    """View redirect đến external URL"""
    return redirect('https://docs.djangoproject.com/')


# ========== Form Handling Views ==========

def form_view(request):
    """View xử lý form"""
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')
        
        if name and email and message:
            # Process form data (in real app, save to database)
            context = {
                'success': True,
                'name': name,
                'email': email,
                'message': message
            }
            return render(request, 'views_practice/form_success.html', context)
        else:
            context = {
                'error': 'All fields are required',
                'name': name,
                'email': email,
                'message': message
            }
            return render(request, 'views_practice/form.html', context)
    
    # GET request - show form
    return render(request, 'views_practice/form.html')


# ========== Custom Error Views ==========

def custom_404_view(request, exception):
    """Custom 404 error view"""
    return render(request, 'views_practice/404.html', status=404)


def custom_500_view(request):
    """Custom 500 error view"""
    return render(request, 'views_practice/500.html', status=500)


def custom_403_view(request, exception):
    """Custom 403 error view"""
    return render(request, 'views_practice/403.html', status=403)


def trigger_500_error(request):
    """View để test 500 error"""
    raise Exception("This is a test 500 error")


# ========== Views Practice Index ==========

def views_index(request):
    """Index page cho views practice"""
    views_examples = [
        {
            'name': 'Simple Views',
            'items': [
                {'title': 'Current DateTime', 'url': 'views_practice:current_datetime', 'description': 'Simple view trả về thời gian hiện tại'},
                {'title': 'Hello World', 'url': 'views_practice:hello', 'description': 'View đơn giản trả về Hello World'},
                {'title': 'View with Parameters', 'url': 'views_practice:view_params', 'description': 'View với parameters từ URL', 'params': ['Django', 25]},
            ]
        },
        {
            'name': 'Error Handling',
            'items': [
                {'title': 'Http404 Exception', 'url': 'views_practice:item_detail', 'description': 'Demo Http404 exception', 'params': [999]},
                {'title': 'Custom 404', 'url': 'views_practice:custom_404', 'description': 'Custom HttpResponseNotFound'},
                {'title': 'Custom Status Code', 'url': 'views_practice:custom_status', 'description': 'HTTP 201 status code'},
                {'title': 'Permission Denied', 'url': 'views_practice:permission_denied', 'description': 'Demo PermissionDenied exception'},
            ]
        },
        {
            'name': 'HTTP Methods',
            'items': [
                {'title': 'Method Specific View', 'url': 'views_practice:method_specific', 'description': 'View chỉ accept GET và POST'},
                {'title': 'All Methods View', 'url': 'views_practice:all_methods', 'description': 'View hiển thị thông tin HTTP method'},
            ]
        },
        {
            'name': 'Async Views',
            'items': [
                {'title': 'Async DateTime', 'url': 'views_practice:async_datetime', 'description': 'Async view example'},
            ]
        },
        {
            'name': 'JSON Responses',
            'items': [
                {'title': 'JSON Response', 'url': 'views_practice:json_response', 'description': 'View trả về JSON'},
                {'title': 'JSON with Params', 'url': 'views_practice:json_user', 'description': 'JSON response với parameters', 'params': [1]},
            ]
        },
        {
            'name': 'Templates',
            'items': [
                {'title': 'Template View', 'url': 'views_practice:template_view', 'description': 'View sử dụng template'},
                {'title': 'Template with Params', 'url': 'views_practice:template_params', 'description': 'Template với parameters', 'params': ['electronics', 123]},
            ]
        },
        {
            'name': 'Redirects',
            'items': [
                {'title': 'Simple Redirect', 'url': 'views_practice:redirect', 'description': 'Redirect đến view khác'},
                {'title': 'Redirect with Params', 'url': 'views_practice:redirect_params', 'description': 'Redirect với parameters'},
                {'title': 'External Redirect', 'url': 'views_practice:redirect_external', 'description': 'Redirect đến external URL'},
            ]
        },
        {
            'name': 'Forms',
            'items': [
                {'title': 'Form Handling', 'url': 'views_practice:form_view', 'description': 'Form processing example'},
            ]
        },
        {
            'name': 'Error Testing',
            'items': [
                {'title': 'Trigger 500 Error', 'url': 'views_practice:trigger_500', 'description': 'Test custom 500 error handler'},
            ]
        }
    ]
    
    context = {
        'title': 'Django Views Practice',
        'views_examples': views_examples
    }
    return render(request, 'views_practice/index.html', context)
