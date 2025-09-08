from django import forms
from django.core.exceptions import ValidationError
from .models import Theme, ThemeVariable
from django.utils.text import slugify
import re
from django.template.loader import engines


def limpar_cache_templates():
    for engine in engines.all():
        if hasattr(engine.engine, 'template_loaders'):
            for loader in engine.engine.template_loaders:
                if hasattr(loader, 'reset'):
                    loader.reset() 


class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta_from_theme = {}

    def clean_upload(self):
        upload = self.cleaned_data.get('upload')
        if upload:
            temp_theme = Theme(upload=upload)
            try:
                temp_theme.clean_upload()
            except ValidationError as e:
                raise ValidationError(e.messages)
        return upload

    def clean(self):
        cleaned_data = super().clean()
        upload = cleaned_data.get('upload')

        nome = cleaned_data.get('nome')
        slug = cleaned_data.get('slug')

        if upload:
            temp_theme = Theme(upload=upload)
            temp_theme.slug = slug or slugify(nome or '')

            try:
                temp_theme.processar_upload()
                limpar_cache_templates()

                # Aplica os metadados ANTES da validação
                self._meta_from_theme = {
                    'nome': temp_theme.nome,
                    'slug': temp_theme.slug,
                    'version': temp_theme.version,
                    'author': temp_theme.author,
                    'descricao': temp_theme.descricao,
                }

                # Atualiza os dados no formulário com os metadados extraídos
                cleaned_data.update(self._meta_from_theme)

            except ValidationError as e:
                self.add_error('upload', e.messages[0] if e.messages else "Erro de validação.")
            except Exception as e:
                self.add_error('upload', f"Erro inesperado: {str(e)}")

        # Após adicionar os metadados, verifique a unicidade dos campos
        nome_final = cleaned_data.get('nome')
        slug_final = cleaned_data.get('slug')

        # Validação de unicidade para 'nome' e 'slug'
        if nome_final and Theme.objects.exclude(pk=self.instance.pk).filter(nome=nome_final).exists():
            self.add_error('upload', f"O tema com nome '{nome_final}' já existe.")

        if slug_final and Theme.objects.exclude(pk=self.instance.pk).filter(slug=slug_final).exists():
            self.add_error('upload', f"O tema com slug '{slug_final}' já existe.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Aplica os metadados extraídos, se existirem
        for field, value in self._meta_from_theme.items():
            setattr(instance, field, value)

        if commit:
            instance.save()

        return instance


class ThemeVariableForm(forms.ModelForm):
    class Meta:
        model = ThemeVariable
        fields = '__all__'

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', nome):
            raise forms.ValidationError(
                "O nome só pode conter letras, números e underscore (_), começando por uma letra ou underscore."
            )
        return nome
