from django import forms
from .models import KYC

class KYCForm(forms.ModelForm):
    class Meta:
        model = KYC
        fields = ['full_name', 'id_type', 'id_number']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full pl-12 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-4 focus:ring-arion-blue/10 transition-all font-medium', 'placeholder': 'As per ID card'}),
            'id_type': forms.Select(attrs={'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-4 focus:ring-arion-blue/10 transition-all font-medium'}),
            'id_number': forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-4 focus:ring-arion-blue/10 transition-all font-medium', 'placeholder': 'Enter ID number'}),
        }
