from django.urls import path
from . import views

app_name = 'views_practice'

urlpatterns = [
    # Index page
    path('', views.views_index, name='index'),
    
    # Simple Views
    path('current-datetime/', views.current_datetime, name='current_datetime'),
    path('hello/', views.simple_hello, name='hello'),
    path('params/<str:name>/<int:age>/', views.view_with_parameters, name='view_params'),
    
    # Error Handling Views
    path('item/<int:item_id>/', views.view_with_404_exception, name='item_detail'),
    path('custom-404/', views.view_with_custom_404, name='custom_404'),
    path('custom-status/', views.view_with_custom_status, name='custom_status'),
    path('permission-denied/', views.view_with_permission_denied, name='permission_denied'),
    
    # HTTP Methods
    path('method-specific/', views.method_specific_view, name='method_specific'),
    path('all-methods/', views.all_methods_view, name='all_methods'),
    
    # Async Views
    path('async-datetime/', views.async_current_datetime, name='async_datetime'),
    
    # JSON Responses
    path('json/', views.json_response_view, name='json_response'),
    path('json/user/<int:user_id>/', views.json_response_with_params, name='json_user'),
    
    # Template Views
    path('template/', views.template_view, name='template_view'),
    path('template/<str:category>/<int:item_id>/', views.template_with_params, name='template_params'),
    
    # Redirects
    path('redirect/', views.redirect_view, name='redirect'),
    path('redirect-params/', views.redirect_with_params, name='redirect_params'),
    path('redirect-external/', views.redirect_external, name='redirect_external'),
    
    # Forms
    path('form/', views.form_view, name='form_view'),
    
    # Error Testing
    path('trigger-500/', views.trigger_500_error, name='trigger_500'),
]
