from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Product, Purchase, UserProfile, Review, Booking


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'products_count']

    def get_products_count(self, obj):
        return obj.products.count()


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    reviews_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'price', 'in_stock', 
            'stock_quantity', 'created_at', 'updated_at', 'tags', 'owner',
            'reviews_count', 'average_rating'
        ]

    def get_reviews_count(self, obj):
        return obj.reviews.count()

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return None


class ProductMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for related products."""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'in_stock', 'category_name']


class PurchaseSerializer(serializers.ModelSerializer):
    purchaser = serializers.StringRelatedField(read_only=True)
    product = ProductMinimalSerializer(read_only=True)

    class Meta:
        model = Purchase
        fields = [
            'id', 'purchaser', 'product', 'quantity', 'total_price', 
            'purchase_date', 'status', 'notes'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user', 'profession', 'location', 'birth_date', 'bio', 
            'website', 'interests'
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='filtering_profile', read_only=True)
    purchases_count = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'date_joined', 'profile', 'purchases_count', 'products_count'
        ]

    def get_purchases_count(self, obj):
        return obj.purchases.count()

    def get_products_count(self, obj):
        return obj.owned_products.count()


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.StringRelatedField(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'product', 'product_name', 'reviewer', 'rating', 'title', 
            'content', 'created_at', 'helpful_votes', 'verified_purchase'
        ]


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'title', 'description', 'start_date', 'end_date',
            'status', 'priority', 'created_at'
        ]