from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from post.models import Post, PostLike, PostComment, CommentLike
from users.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    post_likes_count = serializers.SerializerMethodField(method_name="get_post_likes_count")
    post_comments_count = serializers.SerializerMethodField(method_name="get_post_comments_count")

    class Meta:
        model = Post
        fields = (
            'id', 'author', "image", "caption", "created_time", "post_likes_count",
            "post_comments_count")

    def to_representation(self, instance):
        print("Instance: ", instance)
        instance = super().to_representation(instance)
        instance["success"] = True
        return instance

    @staticmethod
    def get_post_likes_count(obj):
        return obj.likes.count()

    @staticmethod
    def get_post_comments_count(obj):
        return obj.comments.count()


class PostLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ["id", "author"]


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    likes_count = serializers.SerializerMethodField(method_name="get_comment_likes_count")
    author = UserSerializer(read_only=True, required=False)

    class Meta:
        model = PostComment
        fields = ['id', 'author', 'comment', 'created_time', 'likes_count', 'post']

    @staticmethod
    def get_comment_likes_count(obj):
        return obj.likes.count()


class CommentLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = CommentLike
        fields = ["id", "author", "comment"]
