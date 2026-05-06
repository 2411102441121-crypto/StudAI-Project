from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Model untuk daftar matakuliah/materi
class Materi(models.Model):
    nama_matkul = models.CharField(max_length=100)
    jumlah_pdf = models.IntegerField(default=0)

    def __str__(self):
        return self.nama_matkul
    
class Jadwal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True) # Relasi ke User
    TIPE_CHOICES = [
        ('tugas', 'Tugas'),
        ('belajar', 'Kegiatan Belajar'),
    ]
    tipe = models.CharField(max_length=20, choices=TIPE_CHOICES, default='tugas')
    kegiatan = models.CharField(max_length=255)
    waktu_mulai = models.TimeField(null=True, blank=True) # Null untuk Tugas
    waktu_selesai = models.TimeField(null=True, blank=True) # Null untuk Tugas
    jam_deadline = models.TimeField(null=True, blank=True) # Hanya untuk Tugas
    tanggal = models.DateField()

    def __str__(self):
        return f"{self.kegiatan} ({self.tipe})"