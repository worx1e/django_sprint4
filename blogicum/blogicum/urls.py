from django.contrib import admin
from django.urls import path, include
from pages import views as pages_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', pages_views.register, name='registration'),

    path('', include('pages.urls')),
    path('', include('blog.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
