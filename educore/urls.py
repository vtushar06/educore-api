"""
EduCore API — Root URL configuration.

All API endpoints are versioned under /api/v1/.
Admin interface available at /admin/.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.courses.urls")),
    path("api/v1/", include("apps.assessments.urls")),
    path("api/v1/", include("apps.content.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize admin site branding
admin.site.site_header = "EduCore Administration"
admin.site.site_title = "EduCore Admin"
admin.site.index_title = "Dashboard"
