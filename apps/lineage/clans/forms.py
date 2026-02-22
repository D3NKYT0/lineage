from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ClanProfile, RecruitmentApplication

class ClanProfileForm(forms.ModelForm):
    class Meta:
        model = ClanProfile
        fields = ['recruiting', 'motd', 'min_level', 'required_classes', 'playtime_requirements', 'language', 'focus', 'crest_image', 'banner_image']
        widgets = {
            'motd': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'recruiting': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'min_level': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 85}),
            'required_classes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Ex: Bishop, Shillien Elder")}),
            'playtime_requirements': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Ex: 18:00 - 22:00")}),
            'language': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Ex: Português")}),
            'focus': forms.Select(attrs={'class': 'form-select'}),
            'crest_image': forms.FileInput(attrs={'class': 'form-control'}),
            'banner_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class RecruitmentApplicationForm(forms.ModelForm):
    class Meta:
        model = RecruitmentApplication
        fields = ['char_name', 'char_id', 'message']
        widgets = {
            'char_name': forms.HiddenInput(),
            'char_id': forms.HiddenInput(),
            'message': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': _("Conte por que deseja entrar, sua experiência e horários ativos.")})
        }
