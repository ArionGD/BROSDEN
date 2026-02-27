from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'is_anonymous']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'hidden'}),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell us about your experience...',
                'class': 'w-full bg-slate-50 border-2 border-transparent rounded-3xl py-6 px-8 text-sm font-bold text-slate-800 focus:outline-none focus:border-arion-blue-light focus:bg-white transition-all'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'w-5 h-5 rounded border-slate-300 text-arion-blue focus:ring-arion-blue'})
        }
