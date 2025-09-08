from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Solicitation
from .choices import STATUS_CHOICES, CATEGORY_CHOICES, PRIORITY_CHOICES


class SolicitationForm(forms.ModelForm):
    class Meta:
        model = Solicitation
        fields = ['title', 'description', 'category', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Digite o título da sua solicitação')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('Descreva detalhadamente sua solicitação')
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class EventForm(forms.Form):
    action = forms.CharField(
        max_length=255, 
        label=_("Descrição do Evento"),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Descreva o que aconteceu ou a ação tomada')
        })
    )
    image = forms.ImageField(
        required=False, 
        label=_("Imagem (opcional)"),
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        })
    )


class SolicitationStatusForm(forms.Form):
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label=_("Novo Status"),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    assigned_to = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label=_("Atribuir para"),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    comment = forms.CharField(
        max_length=500,
        required=False,
        label=_("Comentário"),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Comentário opcional sobre a mudança de status')
        })
    )

    def __init__(self, *args, **kwargs):
        from apps.main.home.models import User
        super().__init__(*args, **kwargs)
        # Filtra apenas usuários staff para atribuição
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)
