from django import forms
from .models import ShopItem, ShopPackage, PromotionCode
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _


class ShopItemForm(forms.ModelForm):
    class Meta:
        model = ShopItem
        fields = ['nome', 'item_id', 'preco', 'quantidade', 'ativo']
        labels = {
            'nome': _('Item Name'),
            'item_id': _('Item ID'),
            'preco': _('Price'),
            'quantidade': _('Quantity'),
            'ativo': _('Active'),
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Item name')}),
            'item_id': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Item ID')}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Price')}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Quantity')}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ShopPackageForm(forms.ModelForm):
    itens = forms.ModelMultipleChoiceField(
        queryset=ShopItem.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(_("Items"), is_stacked=False),
        label=_("Package Items")
    )

    class Meta:
        model = ShopPackage
        fields = ['nome', 'preco_total', 'ativo', 'promocao', 'itens']
        labels = {
            'nome': _('Package Name'),
            'preco_total': _('Total Price'),
            'ativo': _('Active'),
            'promocao': _('Promotion'),
            'itens': _('Items'),
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Package name')}),
            'preco_total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Total price')}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'promocao': forms.Select(attrs={'class': 'form-control'}),
        }

    class Media:
        css = {'all': ('admin/css/widgets.css',)}
        js = ('admin/js/core.js', 'admin/js/SelectBox.js', 'admin/js/SelectFilter2.js', '/jsi18n/')


class PromotionCodeForm(forms.ModelForm):
    validade = forms.DateTimeField(
        label=_("Expiration Date"),
        required=False,
        input_formats=['%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'placeholder': _('Ex: 2025-04-30 18:00')
            }
        )
    )

    class Meta:
        model = PromotionCode
        fields = ['codigo', 'desconto_percentual', 'validade', 'ativo']
        labels = {
            'codigo': _('Promotion Code'),
            'desconto_percentual': _('Discount (%)'),
            'validade': _('Expiration Date'),
            'ativo': _('Active'),
        }
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Promotion code')}),
            'desconto_percentual': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Discount (%)')}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
