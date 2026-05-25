from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Baris ini SANGAT PENTING untuk mengatasi error 'google_login' not found
    path('accounts/', include('allauth.urls')), 
    path('', include('planner.urls')),
]

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', include('planner.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)