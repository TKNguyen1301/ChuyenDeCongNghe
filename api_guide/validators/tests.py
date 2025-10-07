from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import datetime, date
from .models import CustomerReportRecord, BlogPost, ToDoList, ToDoItem, BillingRecord
from .serializers import (
    CustomerReportSerializer, BlogPostSerializer, BlogPostWithDateValidatorsSerializer,
    ToDoItemSerializer, BillingRecordSerializer, NumberValidationSerializer,
    TimestampedSerializer, even_number, MultipleOf
)
from rest_framework import serializers

User = get_user_model()


class CustomerReportValidatorTests(TestCase):
    """Test unique constraint on CustomerReportRecord reference field."""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
    
    def test_unique_reference_validation(self):
        """Test that duplicate references are rejected."""
        # Create first record
        data1 = {'reference': 'REF001', 'description': 'First report'}
        serializer1 = CustomerReportSerializer(data=data1)
        self.assertTrue(serializer1.is_valid())
        serializer1.save()
        
        # Try to create second record with same reference
        data2 = {'reference': 'REF001', 'description': 'Second report'}
        serializer2 = CustomerReportSerializer(data=data2)
        self.assertFalse(serializer2.is_valid())
        self.assertIn('reference', serializer2.errors)
        self.assertIn('already exists', str(serializer2.errors['reference'][0]))
    
    def test_unique_reference_update_same_instance(self):
        """Test that updating same instance with same reference is allowed."""
        # Create record
        data = {'reference': 'REF002', 'description': 'Original description'}
        serializer = CustomerReportSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        
        # Update same instance
        update_data = {'reference': 'REF002', 'description': 'Updated description'}
        update_serializer = CustomerReportSerializer(instance, data=update_data)
        self.assertTrue(update_serializer.is_valid())


class BlogPostUniqueValidatorTests(TestCase):
    """Test UniqueValidator on BlogPost slug field."""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
    
    def test_unique_slug_validation(self):
        """Test that duplicate slugs are rejected."""
        # Create first blog post
        data1 = {
            'title': 'First Post',
            'slug': 'first-post',
            'content': 'Content of first post'
        }
        serializer1 = BlogPostSerializer(data=data1, context={'request': type('Request', (), {'user': self.user})()})
        self.assertTrue(serializer1.is_valid())
        serializer1.save()
        
        # Try to create second post with same slug
        data2 = {
            'title': 'Second Post',
            'slug': 'first-post',
            'content': 'Content of second post'
        }
        serializer2 = BlogPostSerializer(data=data2, context={'request': type('Request', (), {'user': self.user})()})
        self.assertFalse(serializer2.is_valid())
        self.assertIn('slug', serializer2.errors)


class BlogPostDateValidatorTests(TestCase):
    """Test UniqueForYear, UniqueForMonth, and UniqueForDate validators."""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
    
    def test_unique_for_year_validation(self):
        """Test UniqueForYearValidator."""
        # Create first blog post
        data1 = {
            'title': 'First Post 2023',
            'slug': 'annual-post',
            'content': 'Content of first post',
            'published': datetime(2023, 6, 15, tzinfo=timezone.get_current_timezone())
        }
        serializer1 = BlogPostWithDateValidatorsSerializer(
            data=data1, 
            context={'request': type('Request', (), {'user': self.user})()}
        )
        self.assertTrue(serializer1.is_valid())
        serializer1.save()
        
        # Try to create second post with same slug in same year
        data2 = {
            'title': 'Second Post 2023',
            'slug': 'annual-post',
            'content': 'Content of second post',
            'published': datetime(2023, 12, 25, tzinfo=timezone.get_current_timezone())
        }
        serializer2 = BlogPostWithDateValidatorsSerializer(
            data=data2,
            context={'request': type('Request', (), {'user': self.user})()}
        )
        self.assertFalse(serializer2.is_valid())
        self.assertIn('non_field_errors', serializer2.errors)
        
        # Create post with same slug but different year should work
        data3 = {
            'title': 'Post 2024',
            'slug': 'annual-post',
            'content': 'Content of 2024 post',
            'published': datetime(2024, 1, 1, tzinfo=timezone.get_current_timezone())
        }
        serializer3 = BlogPostWithDateValidatorsSerializer(
            data=data3,
            context={'request': type('Request', (), {'user': self.user})()}
        )
        self.assertTrue(serializer3.is_valid())


class ToDoItemUniqueTogetherTests(TestCase):
    """Test UniqueTogetherValidator on ToDoItem."""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.todo_list = ToDoList.objects.create(name='My List', owner=self.user)
    
    def test_unique_together_list_position(self):
        """Test that list + position combination must be unique."""
        # Create first todo item
        data1 = {
            'list': self.todo_list.id,
            'position': 1,
            'title': 'First task'
        }
        serializer1 = ToDoItemSerializer(data=data1)
        self.assertTrue(serializer1.is_valid())
        serializer1.save()
        
        # Try to create second item with same list + position
        data2 = {
            'list': self.todo_list.id,
            'position': 1,
            'title': 'Second task'
        }
        serializer2 = ToDoItemSerializer(data=data2)
        self.assertFalse(serializer2.is_valid())
        self.assertIn('non_field_errors', serializer2.errors)
        
        # Create item with different position should work
        data3 = {
            'list': self.todo_list.id,
            'position': 2,
            'title': 'Third task'
        }
        serializer3 = ToDoItemSerializer(data=data3)
        self.assertTrue(serializer3.is_valid())


class BillingRecordOptionalFieldTests(TestCase):
    """Test handling of optional fields in validators."""
    
    def test_optional_client_field(self):
        """Test that client field is optional and custom validation works."""
        # Create record without client
        data1 = {
            'date': date.today(),
            'amount': '100.50',
            'description': 'Service fee'
        }
        serializer1 = BillingRecordSerializer(data=data1)
        self.assertTrue(serializer1.is_valid())
        serializer1.save()
        
        # Create another record without client on same date should work
        data2 = {
            'date': date.today(),
            'amount': '200.00',
            'description': 'Another fee'
        }
        serializer2 = BillingRecordSerializer(data=data2)
        self.assertTrue(serializer2.is_valid())
        
        # Create record with client
        data3 = {
            'client': 'ABC Corp',
            'date': date.today(),
            'amount': '300.00',
            'description': 'Consulting'
        }
        serializer3 = BillingRecordSerializer(data=data3)
        self.assertTrue(serializer3.is_valid())
        serializer3.save()
        
        # Try to create duplicate record for same client on same date
        data4 = {
            'client': 'ABC Corp',
            'date': date.today(),
            'amount': '400.00',
            'description': 'More consulting'
        }
        serializer4 = BillingRecordSerializer(data=data4)
        self.assertFalse(serializer4.is_valid())
        self.assertIn('non_field_errors', serializer4.errors)


class CustomValidatorTests(TestCase):
    """Test custom function and class-based validators."""
    
    def test_even_number_validator(self):
        """Test function-based even number validator."""
        # Test valid even number
        try:
            even_number(4)
        except serializers.ValidationError:
            self.fail("even_number validator raised ValidationError for valid even number")
        
        # Test invalid odd number
        with self.assertRaises(serializers.ValidationError):
            even_number(5)
    
    def test_multiple_of_validator(self):
        """Test class-based MultipleOf validator."""
        validator = MultipleOf(5)
        
        # Test valid multiple
        try:
            validator(10)
        except serializers.ValidationError:
            self.fail("MultipleOf validator raised ValidationError for valid multiple")
        
        # Test invalid non-multiple
        with self.assertRaises(serializers.ValidationError):
            validator(7)
    
    def test_number_validation_serializer(self):
        """Test serializer with custom validators."""
        # Valid data
        data1 = {
            'even_number_field': 6,
            'multiple_of_5': 15,
            'multiple_of_10_with_context': 30
        }
        serializer1 = NumberValidationSerializer(data=data1)
        self.assertTrue(serializer1.is_valid())
        
        # Invalid even number
        data2 = {
            'even_number_field': 7,
            'multiple_of_5': 15,
            'multiple_of_10_with_context': 30
        }
        serializer2 = NumberValidationSerializer(data=data2)
        self.assertFalse(serializer2.is_valid())
        self.assertIn('even_number_field', serializer2.errors)
        
        # Invalid multiple of 5
        data3 = {
            'even_number_field': 6,
            'multiple_of_5': 17,
            'multiple_of_10_with_context': 30
        }
        serializer3 = NumberValidationSerializer(data=data3)
        self.assertFalse(serializer3.is_valid())
        self.assertIn('multiple_of_5', serializer3.errors)


class TimestampedSerializerTests(TestCase):
    """Test CreateOnlyDefault validator."""
    
    def test_create_only_default(self):
        """Test that created_at is set only on creation."""
        data = {'name': 'Test Item'}
        serializer = TimestampedSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertIn('created_at', validated_data)
        self.assertIn('updated_at', validated_data)
        self.assertEqual(validated_data['name'], 'Test Item')


class ValidatorAPITests(APITestCase):
    """Integration tests for validator API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
    
    def test_customer_report_api(self):
        """Test CustomerReport API with unique validation."""
        url = '/validators/customer-reports/'
        
        # Create first record
        data1 = {'reference': 'API001', 'description': 'First API test'}
        response1 = self.client.post(url, data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Try to create duplicate
        data2 = {'reference': 'API001', 'description': 'Second API test'}
        response2 = self.client.post(url, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('reference', response2.data)
    
    def test_todo_item_api(self):
        """Test ToDoItem API with unique together validation."""
        # Create todo list first
        list_url = '/validators/todo-lists/'
        list_data = {'name': 'API Test List'}
        list_response = self.client.post(list_url, list_data, format='json')
        self.assertEqual(list_response.status_code, status.HTTP_201_CREATED)
        list_id = list_response.data['id']
        
        # Create first todo item
        item_url = '/validators/todo-items/'
        item_data1 = {
            'list': list_id,
            'position': 1,
            'title': 'First API task'
        }
        response1 = self.client.post(item_url, item_data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Try to create duplicate position in same list
        item_data2 = {
            'list': list_id,
            'position': 1,
            'title': 'Second API task'
        }
        response2 = self.client.post(item_url, item_data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response2.data)
    
    def test_custom_validator_api(self):
        """Test custom validator API endpoint."""
        url = '/validators/validate-numbers/'
        
        # Valid data
        data1 = {
            'even_number_field': 8,
            'multiple_of_5': 25,
            'multiple_of_10_with_context': 40
        }
        response1 = self.client.post(url, data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertIn('message', response1.data)
        
        # Invalid data
        data2 = {
            'even_number_field': 9,  # odd number
            'multiple_of_5': 25,
            'multiple_of_10_with_context': 40
        }
        response2 = self.client.post(url, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('even_number_field', response2.data)
    
    def test_serializer_inspection_api(self):
        """Test serializer introspection endpoint."""
        url = '/validators/inspect-serializers/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that response contains serializer representations
        self.assertIn('customer_report_serializer', response.data)
        self.assertIn('blog_post_serializer', response.data)
        self.assertIn('todo_item_serializer', response.data)
        self.assertIn('customer_reference_field_validators', response.data)


class SerializerIntrospectionTests(TestCase):
    """Test serializer introspection as mentioned in the documentation."""
    
    def test_customer_report_serializer_repr(self):
        """Test CustomerReportSerializer representation shows validators."""
        serializer = CustomerReportSerializer()
        repr_str = repr(serializer)
        
        # Should contain the reference field with UniqueValidator
        self.assertIn('reference', repr_str)
        self.assertIn('CharField', repr_str)
        
        # Check that reference field has validators
        reference_field = serializer.fields['reference']
        self.assertTrue(len(reference_field.validators) > 0)
    
    def test_todo_item_serializer_meta_validators(self):
        """Test ToDoItemSerializer Meta validators."""
        serializer = ToDoItemSerializer()
        
        # Should have UniqueTogetherValidator in Meta.validators
        self.assertTrue(hasattr(serializer.Meta, 'validators'))
        self.assertTrue(len(serializer.Meta.validators) > 0)
        
        # Check validator type
        validator = serializer.Meta.validators[0]
        from rest_framework.validators import UniqueTogetherValidator
        self.assertIsInstance(validator, UniqueTogetherValidator)
