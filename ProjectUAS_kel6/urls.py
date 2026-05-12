from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Baris ini SANGAT PENTING untuk mengatasi error 'google_login' not found
    path('accounts/', include('allauth.urls')), 
    path('', include('planner.urls')),
]

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', include('planner.urls')),

]