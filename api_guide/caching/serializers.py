from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, UserProfile, UserFeed


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'author', 'created_at', 'updated_at', 'published']


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'bio', 'location', 'birth_date', 'avatar']


class UserFeedSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserFeed
        fields = ['id', 'user', 'content', 'created_at', 'feed_type']


class UserSerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()
    feed_items_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'posts_count', 'feed_items_count']

    def get_posts_count(self, obj):
        return obj.posts.count()

    def get_feed_items_count(self, obj):
        return obj.feed_items.count()