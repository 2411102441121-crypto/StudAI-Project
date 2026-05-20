from django import forms
from .models import Jadwal

class JadwalForm(forms.ModelForm):
    class Meta:
        model = Jadwal
        # Tambahkan 'jam_deadline' ke dalam list fields di bawah ini
        fields = ['kegiatan', 'tipe', 'tanggal', 'jam_deadline', 'waktu_mulai', 'waktu_selesai']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'jam_deadline': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'waktu_mulai': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'waktu_selesai': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }