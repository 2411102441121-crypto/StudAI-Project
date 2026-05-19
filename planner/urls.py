from django.contrib import admin
from django.urls import path, include
from planner import views # Gunakan satu import views yang konsisten
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('login/', views.login, name='login'),
    # WAJIB: Tambahkan ini agar Google Login Allauth berfungsi
    path('accounts/', include('allauth.urls')), 

    # Rute aplikasi StudAI Anda
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),
    path('tambah_jadwal/', views.tambah_jadwal, name='tambah_jadwal'),
    path('schedule/', views.schedule, name='schedule'),
    path('edit_jadwal/<int:pk>/', views.edit_jadwal, name='edit_jadwal'),
    path('hapus_jadwal/<int:id>/', views.hapus_jadwal, name='hapus_jadwal'),
    path('ai_chat/', views.ai_chat, name='ai_chat'), # Ini halaman chat utama kamu
    path('ai_chat/get_response/', views.api_chat_response, name='api_chat_response'), # Ini untuk handle API-nya
    path('profil/', views.profil, name='profil'),
    path('logout/', views.logout, name='logout'),


    # Reset Password
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]