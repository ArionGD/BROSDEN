from django import forms
from .models import KYC

COMMON_INPUT_CLASS = 'w-full px-4 py-4 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all font-medium text-slate-800'

class KYCForm(forms.ModelForm):
    class Meta:
        model = KYC
        fields = ['full_name', 'id_type', 'id_number']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full pl-12 pr-4 py-4 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all font-medium text-slate-800', 
                'placeholder': 'As per ID card'
            }),
            'id_type': forms.Select(attrs={'class': COMMON_INPUT_CLASS}),
            'id_number': forms.TextInput(attrs={
                'class': COMMON_INPUT_CLASS, 
                'placeholder': 'Enter ID number'
            }),
        }
