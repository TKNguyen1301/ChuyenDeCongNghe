from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator, UniqueForYearValidator, UniqueForMonthValidator, UniqueForDateValidator
from django.utils import timezone
from .models import CustomerReportRecord, BlogPost, ToDoList, ToDoItem, BillingRecord


class CustomerReportSerializer(serializers.ModelSerializer):
    """
    Basic ModelSerializer demonstrating automatic UniqueValidator generation.
    This matches the example from the documentation.
    """
    class Meta:
        model = CustomerReportRecord
        fields = '__all__'


class BlogPostSerializer(serializers.ModelSerializer):
    """
    Serializer demonstrating explicit UniqueValidator usage.
    """
    slug = serializers.SlugField(
        max_length=100,
        validators=[UniqueValidator(queryset=BlogPost.objects.all())]
    )
    # Demonstrate CurrentUserDefault
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'content', 'published', 'author']


class BlogPostWithDateValidatorsSerializer(serializers.ModelSerializer):
    """
    Serializer demonstrating UniqueForYear, UniqueForMonth, and UniqueForDate validators.
    """
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'content', 'published', 'author']
        validators = [
            UniqueForYearValidator(
                queryset=BlogPost.objects.all(),
                field='slug',
                date_field='published'
            )
        ]


class BlogPostWithWritableDateSerializer(serializers.ModelSerializer):
    """
    Example with writable date field for UniqueForDate validation.
    """
    published = serializers.DateTimeField(required=True)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'content', 'published', 'author']
        validators = [
            UniqueForDateValidator(
                queryset=BlogPost.objects.all(),
                field='slug',
                date_field='published'
            )
        ]


class BlogPostWithReadOnlyDateSerializer(serializers.ModelSerializer):
    """
    Example with read-only date field for UniqueForDate validation.
    """
    published = serializers.DateTimeField(read_only=True, default=timezone.now)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'content', 'published', 'author']
        validators = [
            UniqueForDateValidator(
                queryset=BlogPost.objects.all(),
                field='slug',
                date_field='published'
            )
        ]


class BlogPostWithHiddenDateSerializer(serializers.ModelSerializer):
    """
    Example with hidden date field for UniqueForDate validation.
    """
    published = serializers.HiddenField(default=timezone.now)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'content', 'published', 'author']
        validators = [
            UniqueForDateValidator(
                queryset=BlogPost.objects.all(),
                field='slug',
                date_field='published'
            )
        ]


class ToDoListSerializer(serializers.ModelSerializer):
    """
    Serializer for ToDoList with CurrentUserDefault.
    """
    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = ToDoList
        fields = ['id', 'name', 'owner', 'created_at']


class ToDoItemSerializer(serializers.ModelSerializer):
    """
    Serializer demonstrating UniqueTogetherValidator.
    """
    class Meta:
        model = ToDoItem
        fields = ['id', 'list', 'position', 'title', 'completed', 'created_at']
        validators = [
            UniqueTogetherValidator(
                queryset=ToDoItem.objects.all(),
                fields=['list', 'position']
            )
        ]


class BillingRecordSerializer(serializers.ModelSerializer):
    """
    Serializer demonstrating handling of optional fields.
    This removes the default unique together constraint.
    """
    def validate(self, attrs):
        # Apply custom validation logic here
        client = attrs.get('client')
        date = attrs.get('date')
        
        # Custom validation: if client is provided, check for duplicate billing on same date
        if client and BillingRecord.objects.filter(client=client, date=date).exists():
            raise serializers.ValidationError(
                "A billing record for this client on this date already exists."
            )
        
        return attrs

    class Meta:
        model = BillingRecord
        fields = ['id', 'client', 'date', 'amount', 'description']
        extra_kwargs = {'client': {'required': False}}
        validators = []  # Remove default "unique together" constraint


# Custom validators examples

def even_number(value):
    """
    Function-based validator that ensures a number is even.
    """
    if value % 2 != 0:
        raise serializers.ValidationError('This field must be an even number.')


class MultipleOf:
    """
    Class-based validator that ensures a value is a multiple of a given base.
    """
    def __init__(self, base):
        self.base = base

    def __call__(self, value):
        if value % self.base != 0:
            message = 'This field must be a multiple of %d.' % self.base
            raise serializers.ValidationError(message)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.base == other.base


class MultipleOfWithContext:
    """
    Class-based validator with context access.
    """
    requires_context = True

    def __init__(self, base):
        self.base = base

    def __call__(self, value, serializer_field):
        if value % self.base != 0:
            field_name = getattr(serializer_field, 'field_name', 'field')
            message = f'The {field_name} must be a multiple of {self.base}.'
            raise serializers.ValidationError(message)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.base == other.base


# Example serializers using custom validators

class NumberValidationSerializer(serializers.Serializer):
    """
    Serializer demonstrating custom function and class-based validators.
    """
    even_number_field = serializers.IntegerField(validators=[even_number])
    multiple_of_5 = serializers.IntegerField(validators=[MultipleOf(5)])
    multiple_of_10_with_context = serializers.IntegerField(
        validators=[MultipleOfWithContext(10)]
    )


# Example with CreateOnlyDefault

class TimestampedSerializer(serializers.Serializer):
    """
    Serializer demonstrating CreateOnlyDefault usage.
    """
    name = serializers.CharField(max_length=100)
    created_at = serializers.DateTimeField(
        default=serializers.CreateOnlyDefault(timezone.now)
    )
    updated_at = serializers.DateTimeField(default=timezone.now)