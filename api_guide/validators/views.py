from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import CustomerReportRecord, BlogPost, ToDoList, ToDoItem, BillingRecord
from .serializers import (
    CustomerReportSerializer, BlogPostSerializer, BlogPostWithDateValidatorsSerializer,
    BlogPostWithWritableDateSerializer, BlogPostWithReadOnlyDateSerializer,
    BlogPostWithHiddenDateSerializer, ToDoListSerializer, ToDoItemSerializer,
    BillingRecordSerializer, NumberValidationSerializer, TimestampedSerializer
)

User = get_user_model()


class CustomerReportListCreateView(generics.ListCreateAPIView):
    """
    API view for CustomerReportRecord demonstrating UniqueValidator.
    """
    queryset = CustomerReportRecord.objects.all()
    serializer_class = CustomerReportSerializer


class CustomerReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for individual CustomerReportRecord operations.
    """
    queryset = CustomerReportRecord.objects.all()
    serializer_class = CustomerReportSerializer


class BlogPostListCreateView(generics.ListCreateAPIView):
    """
    API view for BlogPost demonstrating explicit UniqueValidator.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

    def perform_create(self, serializer):
        # Ensure user is set (for demonstration, we'll use first user if no auth)
        if not self.request.user.is_authenticated:
            user = User.objects.first()
            if not user:
                # Create a demo user if none exists
                user = User.objects.create_user('demo_user', 'demo@example.com', 'password')
            serializer.save(author=user)
        else:
            serializer.save()


class BlogPostWithDateValidatorsView(generics.ListCreateAPIView):
    """
    API view demonstrating UniqueForYear validator.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostWithDateValidatorsSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            user = User.objects.first()
            if not user:
                user = User.objects.create_user('demo_user2', 'demo2@example.com', 'password')
            serializer.save(author=user)
        else:
            serializer.save()


class ToDoListView(generics.ListCreateAPIView):
    """
    API view for ToDoList.
    """
    queryset = ToDoList.objects.all()
    serializer_class = ToDoListSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            user = User.objects.first()
            if not user:
                user = User.objects.create_user('demo_user3', 'demo3@example.com', 'password')
            serializer.save(owner=user)
        else:
            serializer.save()


class ToDoItemView(generics.ListCreateAPIView):
    """
    API view demonstrating UniqueTogetherValidator.
    """
    queryset = ToDoItem.objects.all()
    serializer_class = ToDoItemSerializer


class BillingRecordView(generics.ListCreateAPIView):
    """
    API view demonstrating handling of optional fields.
    """
    queryset = BillingRecord.objects.all()
    serializer_class = BillingRecordSerializer


@api_view(['POST'])
def validate_numbers(request):
    """
    API endpoint to demonstrate custom validators.
    """
    serializer = NumberValidationSerializer(data=request.data)
    if serializer.is_valid():
        return Response({
            'message': 'All numbers are valid!',
            'data': serializer.validated_data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def test_timestamps(request):
    """
    API endpoint to demonstrate CreateOnlyDefault.
    """
    serializer = TimestampedSerializer(data=request.data)
    if serializer.is_valid():
        return Response({
            'message': 'Timestamps created!',
            'data': serializer.validated_data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SerializerInspectionView(APIView):
    """
    View to demonstrate serializer introspection as mentioned in the docs.
    """
    def get(self, request):
        # Create instances of serializers to inspect their validators
        customer_serializer = CustomerReportSerializer()
        blog_serializer = BlogPostSerializer()
        todo_serializer = ToDoItemSerializer()
        
        response_data = {
            'customer_report_serializer': str(customer_serializer),
            'blog_post_serializer': str(blog_serializer),
            'todo_item_serializer': str(todo_serializer),
            'customer_reference_field_validators': [
                str(validator) for validator in 
                customer_serializer.fields['reference'].validators
            ] if 'reference' in customer_serializer.fields else [],
            'blog_slug_field_validators': [
                str(validator) for validator in 
                blog_serializer.fields['slug'].validators
            ] if 'slug' in blog_serializer.fields else [],
            'todo_meta_validators': [
                str(validator) for validator in 
                todo_serializer.Meta.validators
            ] if hasattr(todo_serializer.Meta, 'validators') else []
        }
        
        return Response(response_data)
