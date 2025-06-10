from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Notiz


class NotizForm(forms.ModelForm):
    """Form for creating and editing notes."""
    
    class Meta:
        model = Notiz
        fields = ['name', 'inhalt']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name der Notiz eingeben...'
            }),
            'inhalt': CKEditor5Widget(config_name='extends')
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'autofocus': True})


class NotizAttachForm(forms.ModelForm):
    """Form for attaching a note to an object."""
    
    class Meta:
        model = Notiz
        fields = ['name', 'inhalt']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name der Notiz eingeben...'
            }),
            'inhalt': CKEditor5Widget(config_name='extends')
        }
    
    def __init__(self, *args, **kwargs):
        self.content_object = kwargs.pop('content_object', None)
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'autofocus': True})
    
    def save(self, commit=True):
        notiz = super().save(commit=False)
        if self.content_object:
            notiz.content_object = self.content_object
        if commit:
            notiz.save()
        return notiz
