from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module


ModuleFormSet = inlineformset_factory(
    Course,
    Module,
    fields=['title', 'description'],
    can_delete=True,
    extra=1,
    
    widgets={
        'title': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Title',  
            'style': 'margin-bottom: 10px; display:block; white-space:pre-line', 
        }),
        'description': forms.Textarea(attrs={'class': 'form-control',
                                             'style':'margine-top: 10px; display:block'}),
        
    }
)