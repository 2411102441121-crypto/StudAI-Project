from django.shortcuts import render, redirect, get_object_or_404
from .models import Jadwal
from .forms import JadwalForm
from datetime import date
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required # Tambahkan ini agar aman
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatMessage

import requests
import json

@login_required
def home(request):
    if request.method == 'POST':
        form = JadwalForm(request.POST)
        if form.is_valid():
            jadwal_baru = form.save(commit=False)
            jadwal_baru.user = request.user
            jadwal_baru.save()
            return redirect('home')
    else:
        form = JadwalForm()

    # Perbaikan urutan: urutkan berdasarkan tanggal, lalu jam_deadline agar sinkron
    jadwal_terdekat = Jadwal.objects.filter(
        user=request.user, 
        tanggal__gte=date.today()
    ).order_by('tanggal', 'jam_deadline', 'waktu_mulai')[:3]
    
    return render(request, 'home.html', {
        'form': form, 
        'jadwal_terdekat': jadwal_terdekat,
        'nama_user': request.user.username # Agar nama di Halo, {{ nama_user }} muncul
    })

def login(request):
    if request.method == 'POST':
        # Mengambil data dari form secara manual
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
    # Implementasi pendaftaran pengguna baru (opsional)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save() # Menyimpan user baru ke Database (Data Layer)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Akun berhasil dibuat untuk {username}. Silakan login.')
            return redirect('login') # Mengarahkan kembali ke halaman login
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

def tambah_jadwal(request):
    if request.method == 'POST':
        tipe = request.POST.get('tipe')
        kegiatan = request.POST.get('kegiatan')
        tanggal = request.POST.get('tanggal')
        
        # Ambil waktu berdasarkan tipe yang dipilih
        jam_deadline = request.POST.get('jam_deadline') if tipe == 'tugas' else None
        waktu_mulai = request.POST.get('waktu_mulai') if tipe == 'belajar' else None
        waktu_selesai = request.POST.get('waktu_selesai') if tipe == 'belajar' else None

        # Simpan ke Database
        Jadwal.objects.create(
            user=request.user, # Pastikan user tersimpan jika sudah login
            tipe=tipe,
            kegiatan=kegiatan,
            jam_deadline=jam_deadline, # Masuk ke kolom jam_deadline
            waktu_mulai=waktu_mulai, 
            waktu_selesai=waktu_selesai,
            tanggal=tanggal
        )
        return redirect('home')
    
    return render(request, 'tambah_jadwal.html')

# Fungsi Edit
def edit_jadwal(request, pk):
    jadwal = get_object_or_404(Jadwal, pk=pk)
    if request.method == 'POST':
        tipe = request.POST.get('tipe')
        jadwal.tipe = tipe
        jadwal.kegiatan = request.POST.get('kegiatan')
        jadwal.tanggal = request.POST.get('tanggal')
        
        # Ambil data jam_deadline dari form edit
        jam_dl = request.POST.get('jam_deadline')
        jadwal.jam_deadline = jam_dl if jam_dl else None
        
        # Ambil data waktu mulai & selesai
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

def schedule(request):
    # Urutkan berdasarkan waktu mulai agar timeline urut dari pagi ke malam
    semua_jadwal = Jadwal.objects.filter(user=request.user).order_by('waktu_mulai')
    return render(request, 'schedule.html', {'semua_jadwal': semua_jadwal})


@login_required # Memastikan hanya user yang sudah login (seperti Ahmad) yang bisa chat
def ai_chat(request):
    # Ambil semua history chat milik user yang sedang aktif
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
            
            # Setup API DeepSeek
            api_url = "https://api.deepseek.com/chat/completions"
            api_token = "sk-df07db4db82f4045ab245d78cf884cb8"
            headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": user_message}],
                "stream": False
            }
            
            response = requests.post(api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                ai_reply = response.json()["choices"][0]["message"]["content"]
                
                # 2. Simpan balasan AI ke database
                ChatMessage.objects.create(user=request.user, sender='ai', message=ai_reply)
                
                return JsonResponse({"status": "success", "reply": ai_reply})
            else:
                return JsonResponse({"status": "error", "reply": "Server AI sedang sibuk."})
        except Exception as e:
            return JsonResponse({"status": "error", "reply": str(e)})

def profil(request):

    total_tugas = Jadwal.objects.filter(
        user=request.user,
        tipe='tugas'
    ).count()

    total_belajar = Jadwal.objects.filter(
        user=request.user,
        tipe='belajar'
    ).count()

    semua_jadwal = Jadwal.objects.filter(
        user=request.user
    ).count()

    context = {

        'username': request.user.username,

        'email': request.user.email,

        'total_tugas': total_tugas,

        'total_belajar': total_belajar,

        'semua_jadwal': semua_jadwal,
    }

    return render(request, 'profil.html', context)

def logout(request):
    auth_logout(request)
    return redirect('login')