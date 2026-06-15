"""
File ini adalah Migration Django yang dibuat otomatis saat menjalankan:

    python manage.py makemigrations

setelah model ChatMessage ditambahkan ke models.py.

KEGUNAANNYA
----------------
Migration berfungsi sebagai "instruksi" bagi Django untuk membuat,
mengubah, atau menghapus struktur tabel di database.

Dalam kasus ini, migration ini digunakan untuk membuat tabel:

    planner_chatmessage

yang digunakan untuk menyimpan riwayat percakapan antara
User dan AI pada fitur AI Chat.

ALUR KERJANYA:
--------------
models.py
    ↓
makemigrations
    ↓
0005_chatmessage.py
    ↓
migrate
    ↓
MySQL Database

Ketika menjalankan:

    python manage.py migrate

Django membaca file ini lalu membuat tabel ChatMessage
di database MySQL secara otomatis.
"""

# File migration ini dibuat otomatis oleh Django

import django.db.models.deletion

# Digunakan untuk mengambil model User bawaan Django
from django.conf import settings

# Library utama migration dan tipe data database Django
from django.db import migrations, models


# Kelas Migration berisi instruksi perubahan database
class Migration(migrations.Migration):

    # Menentukan migration yang harus dijalankan terlebih dahulu
    dependencies = [

        # Migration ini bergantung pada migration sebelumnya
        # yaitu 0004_jadwal_jam_deadline
        ('planner', '0004_jadwal_jam_deadline'),

        # Memastikan tabel User bawaan Django sudah dibuat
        # sebelum membuat relasi ForeignKey ke User
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    # Daftar operasi database yang akan dilakukan
    operations = [

        # Membuat tabel baru bernama ChatMessage
        migrations.CreateModel(

            # Nama model/tabel yang dibuat
            name='ChatMessage',

            # Daftar kolom dalam tabel
            fields=[

                # Primary Key (ID unik otomatis)
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    )
                ),

                # Menyimpan siapa pengirim pesan
                # Hanya boleh berisi:
                # 'user' = pesan dari pengguna
                # 'ai'   = pesan dari AI
                (
                    'sender',
                    models.CharField(
                        choices=[
                            ('user', 'User'),
                            ('ai', 'AI')
                        ],
                        max_length=10
                    )
                ),

                # Menyimpan isi pesan chat
                # Baik pertanyaan user maupun jawaban AI
                (
                    'message',
                    models.TextField()
                ),

                # Menyimpan waktu pesan dibuat
                # Otomatis terisi saat data dibuat
                (
                    'timestamp',
                    models.DateTimeField(
                        auto_now_add=True
                    )
                ),

                # Relasi ke tabel User Django
                #
                # Setiap pesan chat harus dimiliki oleh
                # satu user yang login.
                #
                # on_delete=CASCADE artinya:
                # jika akun user dihapus,
                # seluruh riwayat chat miliknya
                # akan ikut terhapus.
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL
                    )
                ),
            ],
        ),
    ]