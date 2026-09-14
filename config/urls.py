from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from django.views.generic import TemplateView
from accounts import views
from drf_spectacular.views import (
    SpectacularAPIView,
)


urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('courses/', include('courses.urls')),
    path('notifications/', include('notifications.urls')),
    path('api/', include('accounts.api_urls')),
    path(
        'chat/',
        include('chat.urls')
    ),
    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='api_schema',
    ),

    path(
        'api/swagger/',
        TemplateView.as_view(
            template_name='api/swagger.html'
        ),
        name='swagger_ui',
    ),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)