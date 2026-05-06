from django import forms
from .models import Jadwal

class JadwalForm(forms.ModelForm):
    class Meta:
        model = Jadwal
        fields = ['kegiatan', 'waktu_mulai', 'waktu_selesai', 'tanggal']
        widgets = {
            'waktu_mulai': forms.TimeInput(attrs={'type': 'time'}),
            'waktu_selesai': forms.TimeInput(attrs={'type': 'time'}),
            'tanggal': forms.DateInput(attrs={'type': 'date'}),
        }