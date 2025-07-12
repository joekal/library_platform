"""
URL configuration for library_platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('books.urls')),
    path('api/auth/', include('accounts.urls')),
    path('api/recommendations/', include('recommendations.urls')),
    path('api/groups/', include('groups.urls')),
    path('accounts/', include('allauth.urls')),
    path('tinymce/', include('tinymce.urls')),
]

# Internationalization URLs
urlpatterns += i18n_patterns(
    path('', include('core.urls')),
    path('books/', include('books.urls')),
    path('groups/', include('groups.urls')),
    path('profile/', include('accounts.urls')),
    path('rosetta/', include('rosetta.urls')),
    prefix_default_language=False
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)