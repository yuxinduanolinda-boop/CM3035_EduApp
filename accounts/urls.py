from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('status/create/', views.create_status_update, name='create_status'),
    path(
    'search/',
    views.search_users,
    name='search_users'
    ),
    path(
        'users/<str:username>/',
        views.user_profile,
        name='user_profile'
    ),
]