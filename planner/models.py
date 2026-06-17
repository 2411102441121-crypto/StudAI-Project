from django.db import models
from django.contrib.auth.models import User # Menghubungkan chat dengan user yang login
from django.contrib.auth import logout
from django.conf import settings

# Model untuk daftar matakuliah/materi
class Materi(models.Model):
    nama_matkul = models.CharField(max_length=100)
    jumlah_pdf = models.IntegerField(default=0)

    def __str__(self):
        return self.nama_matkul
    
class Jadwal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    TIPE_CHOICES = [
        ('tugas', 'Tugas'),
        ('belajar', 'Kegiatan Belajar'),
    ]
    tipe = models.CharField(max_length=20, choices=TIPE_CHOICES, default='tugas')
    kegiatan = models.CharField(max_length=255)
    waktu_mulai = models.TimeField(null=True, blank=True)
    waktu_selesai = models.TimeField(null=True, blank=True)
    jam_deadline = models.TimeField(null=True, blank=True)
    tanggal = models.DateField()
    is_selesai = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.kegiatan} ({self.tipe})"
    
# Model untuk menyimpan riwayat percakapan AI Chat
class ChatMessage(models.Model):                    # models.py berfungsi sebagai blueprint atau rancangan tabel database.

    # Pilihan pengirim pesan
    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI'),
    ]

    # Relasi ke tabel User (siapa pemilik chat)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Menyimpan jenis pengirim: user atau AI
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)

    # Menyimpan isi pesan
    message = models.TextField()

    # Menyimpan waktu pesan dibuat otomatis
    timestamp = models.DateTimeField(auto_now_add=True)

    # Tampilan data yang lebih mudah dibaca di Django Admin
    def __str__(self):
        return f"{self.user.username} - {self.sender}: {self.message[:20]}"
    
class FAQ(models.Model):
    pertanyaan = models.CharField(max_length=255)
    jawaban = models.TextField()

    jumlah_digunakan = models.IntegerField(default=0)

    def __str__(self):
        return self.pertanyaan
    
class Folder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama

class Modul(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='files')
    judul = models.CharField(max_length=255)
    isi_file = models.FileField(upload_to='modul_files/') # Jika ingin upload file
    # Atau jika ingin isi teks saja:
    # konten = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.judul