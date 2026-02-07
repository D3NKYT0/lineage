from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import CharacterTransfer
from .services import MarketplaceService
from .character_profile import get_character_profile
from apps.lineage.server.database import LineageDB
from utils.dynamic_import import get_query_class
from utils.resources import get_class_name
from apps.lineage.server.services.account_context import (
    get_active_login,
    get_lineage_template_context,
)

# Importa classes de query dinamicamente
LineageMarketplace = get_query_class("LineageMarketplace")


def marketplace_list(request):
    """
    Lista todos os personagens disponíveis para venda.
    """
    transfers = CharacterTransfer.objects.filter(status='for_sale').select_related('seller')
    
    # Adicionar nome da classe para cada personagem
    for transfer in transfers:
        if transfer.char_class is not None:
            transfer.class_name = get_class_name(transfer.char_class)
        else:
            transfer.class_name = '-'
    
    return render(request, 'marketplace/list.html', {'transfers': transfers})


def character_detail(request, transfer_id):
    """
    Mostra detalhes de um personagem à venda: status completo do L2,
    inventário, equipamento e linha do tempo (biografia do personagem).
    """
    transfer = get_object_or_404(CharacterTransfer, id=transfer_id)
    profile = get_character_profile(transfer)

    context = {
        'transfer': transfer,
        'char_details': profile['char_details'],
        'equipment': profile['equipment'],
        'inventory': profile['inventory'],
        'timeline_events': profile['timeline_events'],
        'has_l2_data': profile['has_l2_data'],
    }
    return render(request, 'marketplace/character_detail.html', context)


@login_required
def sell_character(request):
    """
    Formulário para listar um personagem para venda.
    """
    # Verifica conexão com banco do Lineage
    db = LineageDB()
    if not db.is_connected():
        messages.error(request, _('O banco do jogo está indisponível no momento. Tente novamente mais tarde.'))
        return redirect('marketplace:list')
    
    # Busca personagens do usuário
    characters = []
    active_login = get_active_login(request)
    try:
        account_name = active_login
        characters = LineageMarketplace.get_user_characters(account_name)
        
        # Filtrar personagens que já estão à venda
        chars_on_sale = list(CharacterTransfer.objects.filter(
            status__in=['pending', 'for_sale']
        ).values_list('char_id', flat=True))
        
        # Remove personagens já listados (se houver)
        if characters and chars_on_sale:
            characters = [char for char in characters if char['char_id'] not in chars_on_sale]
        
        # Filtrar personagens com accesslevel > 0 (GMs não podem vender)
        if characters:
            characters = [char for char in characters if char.get('accesslevel', 0) == 0]
            
    except Exception as e:
        messages.warning(request, _('Não foi possível carregar seus personagens. Tente novamente.'))
    
    if request.method == 'POST':
        try:
            char_id = request.POST.get('char_id')
            price = request.POST.get('price')
            currency = request.POST.get('currency', 'BRL')
            notes = request.POST.get('notes', '')
            
            # Validações
            if not char_id or not price:
                raise ValidationError(_('Todos os campos obrigatórios devem ser preenchidos.'))
            
            # Remover formatação de números (pontos, vírgulas, espaços)
            char_id_clean = str(char_id).replace('.', '').replace(',', '').replace(' ', '').strip()
            price_clean = str(price).replace('.', '').replace(',', '.').replace(' ', '').strip()
            
            # Criar a listagem
            transfer = MarketplaceService.list_character_for_sale(
                user=request.user,
                char_id=int(char_id_clean),
                account_name=active_login,
                price=float(price_clean),
                currency=currency,
                notes=notes
            )
            
            messages.success(request, _('Personagem listado com sucesso no marketplace!'))
            return redirect('marketplace:character_detail', transfer_id=transfer.id)
            
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, _('Erro ao listar personagem. Tente novamente.'))
    
    # Converter para garantir compatibilidade com Django template
    if characters:
        characters = list(characters)
    
    context = {
        'characters': characters if characters else [],
    }
    context.update(get_lineage_template_context(request))
    
    return render(request, 'marketplace/sell.html', context)


@login_required
def buy_character(request, transfer_id):
    """
    Processa a compra de um personagem.
    """
    if request.method == 'POST':
        try:
            transfer = MarketplaceService.purchase_character(
                buyer=request.user,
                transfer_id=transfer_id
            )
            messages.success(request, _('Compra realizada com sucesso!'))
            return redirect('marketplace:character_detail', transfer_id=transfer.id)
        except Exception as e:
            messages.error(request, str(e))
    
    return redirect('marketplace:character_detail', transfer_id=transfer_id)


@login_required
def cancel_sale(request, transfer_id):
    """
    Cancela uma venda.
    """
    if request.method == 'POST':
        try:
            MarketplaceService.cancel_sale(transfer_id, request.user)
            messages.success(request, _('Venda cancelada com sucesso!'))
        except Exception as e:
            messages.error(request, str(e))
    
    return redirect('marketplace:my_sales')


@login_required
def my_sales(request):
    """
    Lista as vendas do usuário.
    """
    sales = CharacterTransfer.objects.filter(seller=request.user).order_by('-listed_at')
    
    # Adicionar nome da classe para cada personagem
    for sale in sales:
        if sale.char_class is not None:
            sale.class_name = get_class_name(sale.char_class)
        else:
            sale.class_name = '-'
    
    return render(request, 'marketplace/my_sales.html', {'sales': sales})


@login_required
def my_purchases(request):
    """
    Lista as compras do usuário.
    """
    purchases = CharacterTransfer.objects.filter(buyer=request.user).order_by('-sold_at')
    
    # Adicionar nome da classe para cada personagem
    for purchase in purchases:
        if purchase.char_class is not None:
            purchase.class_name = get_class_name(purchase.char_class)
        else:
            purchase.class_name = '-'
    
    return render(request, 'marketplace/my_purchases.html', {'purchases': purchases})

