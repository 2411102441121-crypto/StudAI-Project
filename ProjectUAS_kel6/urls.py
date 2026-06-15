"""
"Terminal Induk" untuk mengontrol seluruh aplikasi.
(Login Google) adalah sistem akun global yang dipakai untuk seluruh web (bukan cuma milik satu fitur saja)

"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Jalur wajib untuk Google Login / Allauth
    path('accounts/', include('allauth.urls')), 
    
    # Jalur untuk aplikasi planner kamu
    path('', include('planner.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)