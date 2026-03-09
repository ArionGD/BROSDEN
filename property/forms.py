from django import forms
from .models import Property, PropertyImage

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'price', 'property_type', 'address', 'city', 'sqft', 'latitude', 'longitude',
            'contact_name', 'contact_phone', 'availability_date', 'security_deposit',
            'bhk_type', 'floor_number', 'total_floors', 'furnishing_status', 'bathrooms', 'balconies', 'parking_type', 'maintenance_charges', 'amenities',
            'sharing_type', 'gender_preference', 'food_included', 'food_details', 'ac_available', 'laundry_available', 'wifi_available', 'rules_restrictions', 'cleaning_frequency', 'total_capacity'
        ]
        widgets = {
            field: forms.TextInput(attrs={'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-4 focus:ring-blue-100 transition-all font-medium'}) 
            for field in [
                'title', 'price', 'address', 'city', 'sqft', 'latitude', 'longitude',
                'contact_name', 'contact_phone', 'security_deposit',
                'floor_number', 'total_floors', 'bathrooms', 'balconies', 'maintenance_charges',
                'cleaning_frequency', 'total_capacity'
            ]
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common_classes = 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-4 focus:ring-blue-100 transition-all font-medium'
        
        # Textareas
        for field in ['description', 'amenities', 'food_details', 'rules_restrictions']:
            if field in self.fields:
                self.fields[field].widget = forms.Textarea(attrs={'class': common_classes, 'rows': 3})
        
        # Choices
        choice_fields = ['property_type', 'bhk_type', 'furnishing_status', 'parking_type', 'sharing_type', 'gender_preference']
        for field in choice_fields:
            if field in self.fields:
                self.fields[field].widget.attrs.update({'class': common_classes})
        
        # Dates
        if 'availability_date' in self.fields:
            self.fields['availability_date'].widget = forms.DateInput(attrs={'class': common_classes, 'type': 'date'})

class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'hidden', 'accept': 'image/*'})
        }
