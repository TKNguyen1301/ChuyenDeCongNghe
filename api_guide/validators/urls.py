from django.urls import path
from . import views

app_name = 'validators'

urlpatterns = [
    # CustomerReportRecord endpoints
    path('customer-reports/', views.CustomerReportListCreateView.as_view(), name='customer-report-list'),
    path('customer-reports/<int:pk>/', views.CustomerReportDetailView.as_view(), name='customer-report-detail'),
    
    # BlogPost endpoints with different validator configurations
    path('blog-posts/', views.BlogPostListCreateView.as_view(), name='blog-post-list'),
    path('blog-posts-date-validators/', views.BlogPostWithDateValidatorsView.as_view(), name='blog-post-date-validators'),
    
    # ToDoList and ToDoItem endpoints
    path('todo-lists/', views.ToDoListView.as_view(), name='todo-list'),
    path('todo-items/', views.ToDoItemView.as_view(), name='todo-item'),
    
    # BillingRecord endpoint
    path('billing-records/', views.BillingRecordView.as_view(), name='billing-record'),
    
    # Custom validator endpoints
    path('validate-numbers/', views.validate_numbers, name='validate-numbers'),
    path('test-timestamps/', views.test_timestamps, name='test-timestamps'),
    
    # Introspection endpoint
    path('inspect-serializers/', views.SerializerInspectionView.as_view(), name='inspect-serializers'),
]