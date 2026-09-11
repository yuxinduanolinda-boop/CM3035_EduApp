from django.urls import path

from .api import user_list_api


urlpatterns = [
    path('users/', user_list_api, name='user_list_api'),
]