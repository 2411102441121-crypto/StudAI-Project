from django.shortcuts import render, redirect, get_object_or_404
from .models import Jadwal, ChatMessage, Folder, Modul
from .forms import JadwalForm

from datetime import date, datetime, timedelta

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings

import requests
import json

@login_required
def home(request):
    today = date.today()
    
    # --- LOGIKA UNTUK FORM TAMBAH JADWAL (Dari kode lama kamu) ---
    if request.method == 'POST':
        form = JadwalForm(request.POST)
        if form.is_valid():
            jadwal_baru = form.save(commit=False)
            jadwal_baru.user = request.user
            jadwal_baru.save()
            return redirect('home')
    else:
        form = JadwalForm()

    # --- LOGIKA UNTUK PROGRESS BAR (Dinamis) ---
    jadwal_hari_ini = Jadwal.objects.filter(user=request.user, tanggal=today)
    total_tugas = jadwal_hari_ini.count()
    tugas_selesai = jadwal_hari_ini.filter(is_selesai=True).count()
    
    if total_tugas > 0:
        persentase = int((tugas_selesai / total_tugas) * 100)
    else:
        persentase = 0 
        
    # --- LOGIKA UNTUK LIST JADWAL TERDEKAT ---
    jadwal_terdekat = Jadwal.objects.filter(
        user=request.user, 
        tanggal__gte=today
    ).order_by('tanggal', 'jam_deadline', 'waktu_mulai')[:5]

    context = {
        'form': form,
        'nama_user': request.user.username,
        'jadwal_terdekat': jadwal_terdekat,
        'persentase': persentase,
        'today': today,
    }
    return render(request, 'home.html', context)

def login(request):
    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        user = authenticate(request, username=u_name, password=p_word)
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Username atau password salah'})
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save() 
            username = form.cleaned_data.get('username')
            messages.success(request, f'Akun berhasil dibuat untuk {username}. Silakan login.')
            return redirect('login') 
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def tambah_jadwal(request):
    if request.method == 'POST':
        tipe = request.POST.get('tipe')
        kegiatan = request.POST.get('kegiatan')
        tanggal = request.POST.get('tanggal')
        
        jam_deadline = request.POST.get('jam_deadline') if tipe == 'tugas' else None
        waktu_mulai = request.POST.get('waktu_mulai') if tipe == 'belajar' else None
        waktu_selesai = request.POST.get('waktu_selesai') if tipe == 'belajar' else None

        Jadwal.objects.create(
            user=request.user, 
            tipe=tipe,
            kegiatan=kegiatan,
            jam_deadline=jam_deadline, 
            waktu_mulai=waktu_mulai, 
            waktu_selesai=waktu_selesai,
            tanggal=tanggal
        )
        return redirect('home')
    return render(request, 'tambah_jadwal.html')

def edit_jadwal(request, pk):
    jadwal = get_object_or_404(Jadwal, pk=pk)
    if request.method == 'POST':
        tipe = request.POST.get('tipe')
        jadwal.tipe = tipe
        jadwal.kegiatan = request.POST.get('kegiatan')
        jadwal.tanggal = request.POST.get('tanggal')
        
        jam_dl = request.POST.get('jam_deadline')
        jadwal.jam_deadline = jam_dl if jam_dl else None
        
        w_mulai = request.POST.get('waktu_mulai')
        jadwal.waktu_mulai = w_mulai if w_mulai else None
        
        w_selesai = request.POST.get('waktu_selesai')
        jadwal.waktu_selesai = w_selesai if w_selesai else None
        
        jadwal.save()
        return redirect('home')
    return render(request, 'edit_jadwal.html', {'jadwal': jadwal})

def hapus_jadwal(request, id):
    jadwal = get_object_or_404(Jadwal, id=id)
    if request.method == "POST":
        jadwal.delete()
        return redirect('home')
    return redirect('home')

@login_required
def schedule(request):
    today = date.today()
    nama_hari_indo = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    days = []
    
    for i in range(-2, 4):
        target_date = today + timedelta(days=i)
        days.append({
            'nama_hari': nama_hari_indo[target_date.weekday()],
            'tanggal': target_date.day,
            'full_date': target_date,
        })

    semua_jadwal = Jadwal.objects.filter(
        user=request.user,
        tanggal__gte=today
    ).order_by('tanggal', 'waktu_mulai', 'jam_deadline')

    return render(request, 'schedule.html', {
        'days': days,
        'today': today,
        'semua_jadwal': semua_jadwal,
    })

@login_required
def book_main(request):
    # 1. Ambil keyword pencarian 'q' dari parameter URL (?q=...)
    query = request.GET.get('q')
    
    # 2. Filter dasar: Ambil folder milik user yang sedang login
    folders = Folder.objects.filter(user=request.user)

    # 3. Proses jika ada keyword pencarian yang dimasukkan user
    if query:
        folders = folders.filter(nama__icontains=query)

    # Urutkan folder berdasarkan waktu pembuatan terbaru
    folders = folders.order_by('-created_at')

    if request.method == "POST":
        nama_folder = request.POST.get('nama_folder')
        if nama_folder:
            Folder.objects.create(
                user=request.user, 
                nama=nama_folder
            )
            return redirect('/book/')

    return render(request, 'book.html', {
        'folders': folders,
        'query_sekarang': query  # Dikirim balik ke template agar teks di input-box tidak hilang
    })


@login_required
def detail_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    moduls = folder.files.all().order_by('-uploaded_at') 

    if request.method == "POST":
        judul = request.POST.get('judul')
        file_upload = request.FILES.get('file_modul') 
        
        if judul and file_upload:
            Modul.objects.create(
                folder=folder,
                judul=judul,
                isi_file=file_upload
            )
            return redirect('detail_folder', folder_id=folder.id)

    return render(request, 'detail_folder.html', {
        'folder': folder,
        'moduls': moduls
    })

@login_required
def hapus_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    folder.delete()
    return redirect('book_main')

def hapus_modul(request, modul_id):
    if request.method == 'POST':
        modul = get_object_or_404(Modul, id=modul_id)
        folder_id = modul.folder.id 
        modul.delete()
        return redirect('detail_folder', folder_id=folder_id) 

@login_required
def toggle_selesai(request, jadwal_id):
    jadwal = Jadwal.objects.get(id=jadwal_id, user=request.user)
    jadwal.is_selesai = not jadwal.is_selesai 
    jadwal.save()
    return redirect('schedule')

@login_required 
def ai_chat(request):
    history = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    return render(request, 'ai_chat.html', {'history': history})

@csrf_exempt
@login_required
def api_chat_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            # 1. Simpan pesan user ke database
            ChatMessage.objects.create(user=request.user, sender='user', message=user_message)

            # 2. Konfigurasi Google Gemini API
            # Tambahkan "models/" sebelum nama modelnya agar Google mengenali jalurnya
            model_name = "models/gemini-2.5-flash"
            api_token = settings.GEMINI_API_KEY
            
            # Gabungkan menjadi URL endpoint yang utuh
            api_url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_token}"

            headers = {
                "Content-Type": "application/json"
            }

            # 3. Sesuaikan Format Payload JSON untuk Gemini
            # Struktur Gemini: {"contents": [{"parts": [{"text": "pesan"}]}]}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": user_message}
                        ]
                    }
                ]
            }

            print(api_url)

            # 4. Kirim Request ke Google
            response = requests.post(api_url, headers=headers, json=payload)

            print(response.status_code)
            print(response.text)

            if response.status_code == 200:
                response_data = response.json()
                
                # 5. Cara membaca jawaban/output dari JSON Google Gemini
                try:
                    ai_reply = response_data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    ai_reply = "Maaf, sistem gagal membaca respon dari AI."

                # 6. Simpan pesan AI ke database dan kirim kembali ke frontend
                ChatMessage.objects.create(user=request.user, sender='ai', message=ai_reply)
                return JsonResponse({"status": "success", "reply": ai_reply})
            else:
                return JsonResponse({
                    "status": "error",
                    "reply": response.text
                    })

        except Exception as e:
            return JsonResponse({"status": "error", "reply": str(e)})

@login_required
def profil(request):
    today = date.today()
    semua_jadwal = Jadwal.objects.filter(user=request.user)

    total_tugas = semua_jadwal.filter(tipe='tugas').count()
    total_belajar = semua_jadwal.filter(is_selesai=True).count()

    jadwal_aktif = semua_jadwal.filter(tanggal__gte=today)
    total_hari_ini = jadwal_aktif.count()
    selesai_hari_ini = jadwal_aktif.filter(is_selesai=True).count()

    if total_hari_ini > 0:
        progress = int((selesai_hari_ini / total_hari_ini) * 100)
    else:
        progress = 0

    context = {
        'username': request.user.username,
        'email': request.user.email,
        'total_tugas': total_tugas,
        'total_belajar': total_belajar,
        'progress': progress,
    }
    return render(request, 'profil.html', context)

def logout(request):
    auth_logout(request)
    return redirect('login')