from rest_framework.urls import path
from post.views import PostListAPIView, PostCreateAPIView, PostUpdateAPIView, PostRetrieveView, PostDeleteView, \
    PostCommentListAPIView, CreatePostCommentView, PostLikeListView, CommentLikeListView, CreateDeletePostLikeView, \
    CreateDeleteCommentLikeView

urlpatterns = [
    path('posts/', PostListAPIView.as_view()),
    path('create-post/', PostCreateAPIView.as_view()),
    path('update-post/<uuid:pk>/', PostUpdateAPIView.as_view()),
    path('get-post/<uuid:pk>/', PostRetrieveView.as_view()),
    path('delete-post/<uuid:pk>/', PostDeleteView.as_view()),

    path('posts/<uuid:pk>/comments/', PostCommentListAPIView.as_view()),
    path('posts/<uuid:pk>/comments/create/', CreatePostCommentView.as_view()),
    path('posts/<uuid:pk>/comment/likes/', CommentLikeListView.as_view()),
    path('posts/<uuid:pk>/comment/create-delete-like/', CreateDeleteCommentLikeView.as_view()),

    path('posts/<uuid:pk>/likes/', PostLikeListView.as_view()),
    path('posts/<uuid:pk>/create-delete-like/', CreateDeletePostLikeView.as_view()),

]
