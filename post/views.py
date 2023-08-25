from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from post.models import Post, PostComment, PostLike, CommentLike
from post.serializers import PostSerializer, CommentSerializer, PostLikeSerializer, CommentLikeSerializer
from shared.custom_methods import CustomPagination


# Create your views here.
class PostListAPIView(ListAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    serializer_class = PostSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()


class PostCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            data = {"message": "Post has been created successfully!", "data": serializer.data}
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_201_CREATED)


class PostUpdateAPIView(APIView):
    serializer_class = PostSerializer

    def put(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(instance=post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = serializer.to_representation(post)
            data['message'] = "Your post has been updated successfully!"
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostRetrieveView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    serializer_class = PostSerializer

    def get(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(post)
        data = serializer.to_representation(post)
        data['message'] = "The post has been retrieved successfully!"
        return Response(data, status=status.HTTP_200_OK)


class PostDeleteView(APIView):
    serializer_class = PostSerializer

    def delete(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
            post.delete()
        except ObjectDoesNotExist:
            return Response({'success': False, "message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        data = {'success': True, 'message': "The post has been removed successfully!"}
        return Response(data, status=status.HTTP_200_OK)


class PostCommentListAPIView(ListAPIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = CommentSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostComment.objects.filter(post__id=post_id)
        return queryset


class CreatePostCommentView(CreateAPIView):
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        serializer.save(author=self.request.user, post_id=post_id)


class PostLikeListView(ListAPIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = PostLikeSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostLike.objects.filter(post__id=post_id)
        return queryset


class CreateDeletePostLikeView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            obj = PostLike.objects.get(author=request.user, post__id=self.kwargs["pk"])
            obj.delete()
            return Response({
                "success": True,
                "message": "LIKE has been removed!"
            }, status=status.HTTP_201_CREATED)

        except ObjectDoesNotExist:
            post = Post.objects.get(id=kwargs['pk'])
            author = request.user
            obj = PostLike.objects.create(author=author, post=post)
            serializer = PostLikeSerializer(obj)
            return Response({
                "success": True,
                "message": f"You succeeded in liking this post",
                "data": serializer.data
            })


class CommentLikeListView(ListAPIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = CommentLikeSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        comment_id = self.kwargs['pk']
        queryset = CommentLike.objects.filter(comment_id=comment_id)
        return queryset


class CreateDeleteCommentLikeView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            obj = CommentLike.objects.get(author=request.user, comment__id=self.kwargs["pk"])
            obj.delete()
            return Response({
                "success": True,
                "message": "LIKE has been removed successfully!"
            }, status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist:
            comment = PostComment.objects.get(id=kwargs['pk'])
            author = request.user
            obj = CommentLike.objects.create(author=author, comment=comment)
            serializer = PostLikeSerializer(obj)
            return Response({
                "success": True,
                "message": f"You succeeded in liking this comment",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
