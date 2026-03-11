from django import forms
from .models import Property, PropertyImage

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'unit_number', 'description', 'property_type', 'total_capacity', 'bed_count', 'sqft', 'bedrooms', 'bathrooms',
            'furnishing_status', 'floor_number', 'total_floors', 'balconies', 'parking_type',
            'sharing_type', 'gender_preference', 'is_for_students', 'is_for_professionals', 'available_from',
            'ac_available', 'has_geyser', 'has_wardrobe', 'has_study_table', 
            'has_workspace_desk', 'has_ergonomic_chair',
            'has_washing_machine', 'has_refrigerator', 'has_stove', 'has_microwave',
            'has_coffee_maker', 'has_toaster', 'has_induction_plate',
            'extra_amenities', 'food_provided', 'provides_breakfast', 'provides_lunch', 'provides_dinner', 'diet_type',
            'laundry_service', 'wifi_available', 'wifi_speed', 'has_cctv', 'has_biometric', 'has_security_guard',
            'has_smoke_alarm', 'has_carbon_monoxide_alarm', 'has_fire_extinguisher', 'has_first_aid_kit', 'has_emergency_exit_plan',
            'visitor_policy', 'curfew_time', 'smoking_allowed', 'alcohol_allowed', 'pets_allowed', 'non_veg_allowed', 'extra_house_rules',
            'price', 'security_deposit', 'electricity_included', 'water_included', 'maintenance_included', 'wifi_included', 'lock_in_period', 'notice_period', 
            'electricity_bill', 'property_tax_slip', 'video_url',
            'contact_name', 'contact_phone', 'city', 'address', 'latitude', 'longitude', 'nearby_landmarks', 'connectivity_info'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common_class = 'w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-4 focus:ring-blue-100 transition-all font-medium placeholder-slate-300'
        checkbox_class = 'w-5 h-5 rounded border-slate-300 text-blue-600 focus:ring-blue-500 transition-all'
        
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': checkbox_class})
            elif isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.EmailInput, forms.URLInput)):
                field.widget.attrs.update({'class': common_class})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': common_class})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': common_class, 'rows': 3})
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.update({'class': 'hidden'}) # Styled manually in template

        if 'available_from' in self.fields:
            self.fields['available_from'].widget = forms.DateInput(attrs={'class': common_class, 'type': 'date'})
        
        # Friendly help texts/placeholders
        if 'nearby_landmarks' in self.fields:
            self.fields['nearby_landmarks'].widget.attrs['placeholder'] = 'e.g., 500m from Alpha One Mall...'
        if 'connectivity_info' in self.fields:
            self.fields['connectivity_info'].widget.attrs['placeholder'] = 'e.g., 10 mins walk from Metro Station...'
        if 'curfew_time' in self.fields:
            self.fields['curfew_time'].widget.attrs['placeholder'] = 'e.g., 11:00 PM or No Curfew'
        if 'extra_amenities' in self.fields:
            self.fields['extra_amenities'].widget.attrs['placeholder'] = 'e.g., Private Terrace, Dedicated workspace, Rooftop garden...'
        if 'extra_house_rules' in self.fields:
            self.fields['extra_house_rules'].widget.attrs['placeholder'] = 'e.g., No parties, Quiet hours after 10 PM, ID required for visitors...'

class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'hidden', 'accept': 'image/*'})
        }
