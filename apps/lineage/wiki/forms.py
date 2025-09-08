from django import forms
from django.utils.translation import gettext_lazy as _
from .models import WikiPage, WikiSection, WikiUpdate, WikiEvent

class WikiPageForm(forms.ModelForm):
    class Meta:
        model = WikiPage
        fields = [
            'title_en', 'title_es', 'title_pt',
            'content_en', 'content_es', 'content_pt',
            'slug', 'order', 'is_active'
        ]
        widgets = {
            'content_en': forms.Textarea(attrs={'rows': 10}),
            'content_es': forms.Textarea(attrs={'rows': 10}),
            'content_pt': forms.Textarea(attrs={'rows': 10}),
        }

class WikiSectionForm(forms.ModelForm):
    class Meta:
        model = WikiSection
        fields = [
            'page',
            'title_en', 'title_es', 'title_pt',
            'content_en', 'content_es', 'content_pt',
            'order', 'is_active'
        ]
        widgets = {
            'content_en': forms.Textarea(attrs={'rows': 10}),
            'content_es': forms.Textarea(attrs={'rows': 10}),
            'content_pt': forms.Textarea(attrs={'rows': 10}),
        }

class WikiUpdateForm(forms.ModelForm):
    class Meta:
        model = WikiUpdate
        fields = [
            'version', 'release_date',
            'content_en', 'content_es', 'content_pt',
            'is_active'
        ]
        widgets = {
            'content_en': forms.Textarea(attrs={'rows': 10}),
            'content_es': forms.Textarea(attrs={'rows': 10}),
            'content_pt': forms.Textarea(attrs={'rows': 10}),
            'release_date': forms.DateInput(attrs={'type': 'date'}),
        }

class WikiEventForm(forms.ModelForm):
    class Meta:
        model = WikiEvent
        fields = [
            'title_en', 'title_es', 'title_pt',
            'event_type',
            'description_en', 'description_es', 'description_pt',
            'schedule_en', 'schedule_es', 'schedule_pt',
            'requirements_en', 'requirements_es', 'requirements_pt',
            'rewards_en', 'rewards_es', 'rewards_pt',
            'is_active'
        ]
        widgets = {
            'description_en': forms.Textarea(attrs={'rows': 5}),
            'description_es': forms.Textarea(attrs={'rows': 5}),
            'description_pt': forms.Textarea(attrs={'rows': 5}),
            'requirements_en': forms.Textarea(attrs={'rows': 5}),
            'requirements_es': forms.Textarea(attrs={'rows': 5}),
            'requirements_pt': forms.Textarea(attrs={'rows': 5}),
            'rewards_en': forms.Textarea(attrs={'rows': 5}),
            'rewards_es': forms.Textarea(attrs={'rows': 5}),
            'rewards_pt': forms.Textarea(attrs={'rows': 5}),
        } 