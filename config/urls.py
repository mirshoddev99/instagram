
from django.contrib import admin
from django.urls import path, include

from api.views import docs_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', docs_view, name='api'),
    path('users/', include('users.urls')),
    path('post/', include('post.urls')),
]
