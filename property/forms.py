from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'description', 'price', 'property_type', 'address', 'city', 'bedrooms', 'bathrooms', 'sqft', 'latitude', 'longitude', 'security_deposit_months', 'contract_fee_percentage']
        widgets = {
            field: forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-4 focus:ring-blue-100 transition-all font-medium'}) 
            for field in ['title', 'price', 'address', 'city', 'bedrooms', 'bathrooms', 'sqft', 'latitude', 'longitude', 'security_deposit_months', 'contract_fee_percentage']
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-4 focus:ring-blue-100 transition-all font-medium', 'rows': 4})
        self.fields['property_type'].widget.attrs.update({'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-4 focus:ring-blue-100 transition-all font-medium'})
