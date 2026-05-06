from django.contrib import admin
from .models import Materi, Jadwal

# Register your models here.
admin.site.register(Materi)

@admin.register(Jadwal)
class JadwalAdmin(admin.ModelAdmin):
    # Menampilkan kolom-kolom ini di daftar list admin
    list_display = ('kegiatan', 'tipe', 'tanggal', 'waktu_mulai', 'waktu_selesai')
    
    # Menambahkan filter di sisi kanan agar mudah mencari berdasarkan tipe
    list_filter = ('tipe', 'tanggal')
    
    # Menambahkan kolom pencarian berdasarkan nama kegiatan
    search_fields = ('kegiatan',)