from django import forms
from .models import Apoiador


class ApoiadorForm(forms.ModelForm):
    class Meta:
        model = Apoiador
        fields = ['nome_publico', 'descricao', 'link_twitch', 'link_youtube', 'imagem']


class SolicitarComissaoForm(forms.Form):
    valor = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)


class ImagemApoiadorForm(forms.ModelForm):
    class Meta:
        model = Apoiador
        fields = ['imagem']
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
