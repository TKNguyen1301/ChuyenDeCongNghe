from rest_framework import serializers
from .models import (
    Product, Order, OrderItem, Article, Comment, 
    Billing, Account
)


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model.
    """
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 
                 'stock_quantity', 'created', 'updated']
        read_only_fields = ['id', 'created', 'updated']


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model.
    """
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'unit_price', 'created']
        read_only_fields = ['id', 'created']


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model with nested order items.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    customer_username = serializers.CharField(source='customer.username', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_username', 'status', 'total_amount', 
                 'order_date', 'shipping_address', 'created', 'items']
        read_only_fields = ['id', 'order_date', 'created']


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    """
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'author_username', 'content', 'created']
        read_only_fields = ['id', 'created']


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for Article model with comments count.
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'author_username', 
                 'slug', 'published', 'view_count', 'created', 'updated', 'comments_count']
        read_only_fields = ['id', 'created', 'updated']

    def get_comments_count(self, obj):
        return obj.comments.count()


class ArticleDetailSerializer(ArticleSerializer):
    """
    Detailed article serializer with comments.
    """
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(ArticleSerializer.Meta):
        fields = ArticleSerializer.Meta.fields + ['comments']


class BillingSerializer(serializers.ModelSerializer):
    """
    Serializer for Billing model - used in documentation examples.
    """
    customer_username = serializers.CharField(source='customer.username', read_only=True)

    class Meta:
        model = Billing
        fields = ['id', 'customer', 'customer_username', 'amount', 
                 'billing_date', 'description', 'paid', 'created']
        read_only_fields = ['id', 'created']


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for Account model - used in API examples.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Account
        fields = ['id', 'user', 'user_username', 'user_email', 'account_number', 
                 'balance', 'account_type', 'created', 'is_active']
        read_only_fields = ['id', 'created']


# Minimal serializers for testing different response formats
class MinimalProductSerializer(serializers.ModelSerializer):
    """
    Minimal product serializer for testing custom pagination response formats.
    """
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category']


class MinimalAccountSerializer(serializers.ModelSerializer):
    """
    Minimal account serializer matching the documentation examples.
    """
    class Meta:
        model = Account
        fields = ['id', 'account_number', 'balance', 'account_type']