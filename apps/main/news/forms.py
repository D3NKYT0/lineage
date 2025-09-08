from django import forms
from .models import News, NewsTranslation
from django_ckeditor_5.widgets import CKEditor5Widget
from django.utils.translation import gettext_lazy as _


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['slug', 'image', 'is_published', 'is_private']
        labels = {
            'slug': _('Slug'),
            'image': _('Image'),
            'is_published': _('Published'),
            'is_private': _('Private'),
        }
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }
        

class NewsTranslationForm(forms.ModelForm):
    class Meta:
        model = NewsTranslation
        fields = ['language', 'title', 'content', 'summary']
        labels = {
            'language': _('Language'),
            'title': _('Title'),
            'content': _('Content'),
            'summary': _('Summary'),
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name="extends"),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        language = kwargs.pop('language', None)
        super(NewsTranslationForm, self).__init__(*args, **kwargs)
        if language:
            self.fields['language'].initial = language
