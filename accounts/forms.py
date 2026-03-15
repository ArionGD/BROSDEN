from django import forms
from .models import User, KYC

I_CLASS = 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all text-slate-800 font-medium'
T_CLASS = 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all text-slate-800 font-medium resize-none'


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': I_CLASS,
        'placeholder': '••••••••'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': I_CLASS,
        'placeholder': '••••••••'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': I_CLASS, 'placeholder': 'Enter your email'}),
            'role': forms.Select(attrs={'class': I_CLASS}),
            'phone_number': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'Phone number'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class KYCForm(forms.ModelForm):
    class Meta:
        model = KYC
        fields = [
            # Common
            'full_name', 'date_of_birth', 'permanent_address', 'mobile_number', 'email_address',
            'id_type', 'id_number', 'pan_number',
            'passport_photo', 'aadhaar_image', 'pan_image',
            # Tenant-specific
            'tenant_type', 'occupation', 'employer_name', 'employer_address', 'monthly_income',
            'emergency_contact_name', 'emergency_contact_relation', 'emergency_contact_phone',
            'home_state',
            # Owner-specific
            'ownership_proof', 'property_tax_receipt', 'property_address',
            'property_type', 'property_size', 'amenities_list',
            'bank_account_name', 'bank_account_number', 'bank_ifsc',
            'co_owner_name', 'co_owner_contact',
        ]
        widgets = {
            # Common
            'full_name': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'As on government ID'}),
            'date_of_birth': forms.DateInput(attrs={'class': I_CLASS, 'type': 'date'}),
            'permanent_address': forms.Textarea(attrs={'class': T_CLASS, 'rows': 3, 'placeholder': 'Full permanent/registered address'}),
            'mobile_number': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': '+91 XXXXX XXXXX (Aadhaar-linked)'}),
            'email_address': forms.EmailInput(attrs={'class': I_CLASS, 'placeholder': 'your@email.com'}),
            'id_type': forms.Select(attrs={'class': I_CLASS}),
            'id_number': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'ID document number'}),
            'pan_number': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'ABCDE1234F', 'style': 'text-transform:uppercase'}),
            # Tenant
            'tenant_type': forms.RadioSelect(attrs={'class': 'hidden'}),
            'occupation': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'e.g., Software Engineer'}),
            'employer_name': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'Employer / College / Guardian Name'}),
            'employer_address': forms.Textarea(attrs={'class': T_CLASS, 'rows': 2, 'placeholder': 'Office / College / Home address'}),
            'monthly_income': forms.NumberInput(attrs={'class': I_CLASS, 'placeholder': 'Monthly income or allowance in ₹'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'Emergency contact name'}),
            'emergency_contact_relation': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'e.g., Father, Spouse'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': '+91 XXXXX XXXXX'}),
            'home_state': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'e.g., Bihar, Uttar Pradesh'}),
            # Owner
            'property_address': forms.Textarea(attrs={'class': T_CLASS, 'rows': 3, 'placeholder': 'Flat/Plot No., Floor, Building, Locality, City, Pincode'}),
            'property_type': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'e.g., 2BHK Apartment'}),
            'property_size': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'e.g., 850 sq.ft'}),
            'amenities_list': forms.Textarea(attrs={'class': T_CLASS, 'rows': 3, 'placeholder': 'Fan x3, AC x1, Geyser... (for agreement)'}),
            'bank_account_name': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'Account holder name'}),
            'bank_account_number': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'Bank account number'}),
            'bank_ifsc': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'e.g., SBIN0001234', 'style': 'text-transform:uppercase'}),
            'co_owner_name': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'Co-owner full name (if any)'}),
            'co_owner_contact': forms.TextInput(attrs={'class': I_CLASS, 'placeholder': 'Co-owner contact number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Explicitly mark secondary fields as NOT required to allow partial submissions
        for field_name, field in self.fields.items():
            if field_name != 'full_name':
                field.required = False


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': I_CLASS}),
            'last_name': forms.TextInput(attrs={'class': I_CLASS}),
            'email': forms.EmailInput(attrs={'class': I_CLASS}),
            'phone_number': forms.TextInput(attrs={'class': I_CLASS}),
            'profile_photo': forms.FileInput(attrs={'class': I_CLASS, 'accept': 'image/*'}),
        }
