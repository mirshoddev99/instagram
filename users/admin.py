from django.contrib import admin
from .models import User, UserConfirmation  # Make sure to import your models


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'username', 'phone_number']


@admin.register(UserConfirmation)
class UserConfirmationAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'verify_type', 'expiration_time']
