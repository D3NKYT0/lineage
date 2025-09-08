from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import FilteredSelectMultiple
from apps.lineage.games.models import *


class BoxTypeAdminForm(forms.ModelForm):
    class Meta:
        model = BoxType
        fields = '__all__'

    allowed_items = forms.ModelMultipleChoiceField(
        queryset=Item.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(_("Itens Permitidos"), is_stacked=False)
    )


class BoxTypeForm(forms.ModelForm):

    allowed_items = forms.ModelMultipleChoiceField(
        queryset=Item.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(_("Itens Permitidos"), is_stacked=False)
    )

    class Media:
        css = {
            'all': ('/static/admin/css/widgets.css',),
        }
        js = ('/admin/jsi18n',)

    class Meta:
        model = BoxType
        fields = [
            'name',
            'price',
            'boosters_amount',
            'chance_common',
            'chance_rare',
            'chance_epic',
            'chance_legendary',
            'max_epic_items',
            'max_legendary_items',
            'allowed_items',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'boosters_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'chance_common': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'chance_rare': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'chance_epic': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'chance_legendary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'max_epic_items': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_legendary_items': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Nome da Caixa'),
            'price': _('Preço (R$)'),
            'boosters_amount': _('Quantidade de Boosters'),
            'chance_common': _('Chance Comum (%)'),
            'chance_rare': _('Chance Rara (%)'),
            'chance_epic': _('Chance Épica (%)'),
            'chance_legendary': _('Chance Lendária (%)'),
            'max_epic_items': _('Máximo de Itens Épicos'),
            'max_legendary_items': _('Máximo de Itens Lendários'),
            'allowed_items': _('Itens Permitidos'),
        }

    def clean(self):
        cleaned_data = super().clean()
        chance_common = cleaned_data.get('chance_common', 0)
        chance_rare = cleaned_data.get('chance_rare', 0)
        chance_epic = cleaned_data.get('chance_epic', 0)
        chance_legendary = cleaned_data.get('chance_legendary', 0)

        total_chance = chance_common + chance_rare + chance_epic + chance_legendary
        if total_chance != 100:
            raise ValidationError(_("A soma das chances deve ser exatamente 100%. Soma atual: {}").format(total_chance))

        return cleaned_data


class BoxForm(forms.ModelForm):
    class Meta:
        model = Box
        fields = ['user', 'box_type']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'box_type': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'user': _('Usuário'),
            'box_type': _('Tipo de Caixa'),
        }


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'enchant', 'item_id', 'image', 'description', 'rarity', 'can_be_populated']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'enchant': forms.NumberInput(attrs={'class': 'form-control'}),
            'item_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rarity': forms.Select(attrs={'class': 'form-control'}),
            'can_be_populated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': _('Nome do Item'),
            'enchant': _('Enchant'),
            'item_id': _('ID do Item'),
            'image': _('Imagem'),
            'description': _('Descrição'),
            'rarity': _('Raridade'),
            'can_be_populated': _('Pode ser populado em caixas'),
        }
