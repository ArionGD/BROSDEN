from django import forms
from .models import User

COMMON_INPUT_CLASS = 'w-full pl-12 pr-4 py-4 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all font-medium text-slate-800'

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': COMMON_INPUT_CLASS,
        'placeholder': '••••••••'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': COMMON_INPUT_CLASS,
        'placeholder': '••••••••'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': COMMON_INPUT_CLASS,
                'placeholder': 'Choose a username'
            }),
            'email': forms.EmailInput(attrs={
                'class': COMMON_INPUT_CLASS,
                'placeholder': 'Enter your email'
            }),
            'role': forms.Select(attrs={
                'class': COMMON_INPUT_CLASS
            }),
            'phone_number': forms.TextInput(attrs={
                'class': COMMON_INPUT_CLASS,
                'placeholder': 'Phone number'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
