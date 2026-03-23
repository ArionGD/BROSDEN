from django import forms
from .models import PropertyReview, TenantReview

class PropertyReviewForm(forms.ModelForm):
    class Meta:
        model = PropertyReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'hidden'}),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell us about your property experience...',
                'class': 'w-full bg-slate-50 border-2 border-transparent rounded-3xl py-6 px-8 text-sm font-bold text-slate-800 focus:outline-none focus:border-arion-blue-light focus:bg-white transition-all'
            }),
        }

class TenantReviewForm(forms.ModelForm):
    class Meta:
        model = TenantReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'hidden'}),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell us about the tenant...',
                'class': 'w-full bg-slate-50 border-2 border-transparent rounded-3xl py-6 px-8 text-sm font-bold text-slate-800 focus:outline-none focus:border-arion-blue-light focus:bg-white transition-all'
            }),
        }
