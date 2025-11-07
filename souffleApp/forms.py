from django import forms
from .models import Review, SouffleApp

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

class CursoForm(forms.ModelForm):
    class Meta:
        model = SouffleApp
        fields = ['title', 'description', 'long_description', 'duration', 'learning_outcomes', 'materials', 'ingredients', 'price', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'long_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'duration': forms.TextInput(attrs={'class': 'form-control'}),
            'learning_outcomes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'materials': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ingredients': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class HorarioForm(forms.ModelForm):
    class Meta:
        model = __import__('souffleApp.models', fromlist=['Horario']).Horario
        fields = ['fecha', 'hora', 'cupos']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'cupos': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }