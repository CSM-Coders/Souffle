from django import forms

# Convertir a ModelForm para Review
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Escribe tu reseña...'
            }),
            'rating': forms.Select(attrs={'class': 'form-select'}, choices=[('', 'Calificación (opcional)')] + [(i, str(i)) for i in range(1,6)])
        }
        labels = {
            'content': '',
            'rating': ''
        }