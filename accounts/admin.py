from django.contrib import admin

from .models import StatusUpdate, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'full_name')

@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'content')