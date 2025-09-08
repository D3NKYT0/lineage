from django.shortcuts import render, get_object_or_404
from ..models import *
from apps.main.home.decorator import conditional_otp_required
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
import random
from decimal import Decimal
from apps.lineage.wallet.models import Wallet
from apps.lineage.wallet.signals import aplicar_transacao
from apps.lineage.inventory.models import Inventory, InventoryLog, InventoryItem
from ..services.box_opening import open_box
from ..services.box_populate import populate_box_with_items
from django.db import transaction
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _


def parse_int(value, default=0):
    try:
        return int(str(value).replace('.', '').replace(',', ''))
    except (ValueError, TypeError):
        return default


@conditional_otp_required
def spin_ajax(request):
    if request.user.fichas <= 0:
        return JsonResponse({'error': _('Você não tem fichas suficientes.')}, status=400)

    prizes = list(Prize.objects.all())
    if not prizes:
        return JsonResponse({'error': _('Nenhum prêmio disponível.')}, status=400)

    # Adicione a opção de falha
    fail_chance = 20  # Representa 20% de chance de falhar
    total_weight = sum(p.weight for p in prizes)
    fail_weight = total_weight * (fail_chance / (100 - fail_chance))

    choices = prizes + [None]  # `None` representa a falha
    weights = [p.weight for p in prizes] + [fail_weight]

    chosen = random.choices(choices, weights=weights, k=1)[0]

    # Deduz uma ficha
    request.user.fichas -= 1
    request.user.save()

    if chosen is None:
        return JsonResponse({'fail': True, 'message': _('Você não ganhou nenhum prêmio.')})

    SpinHistory.objects.create(user=request.user, prize=chosen)

    # Certifique-se de que o usuário tenha uma bag
    bag, created = Bag.objects.get_or_create(user=request.user)

    # Verifica se o item já existe na bag (mesma id + enchant)
    bag_item, created = BagItem.objects.get_or_create(
        bag=bag,
        item_id=chosen.item_id,
        enchant=chosen.enchant,
        defaults={
            'item_name': chosen.name,
            'quantity': 1,
        }
    )

    if not created:
        bag_item.quantity += 1
        bag_item.save()

    return JsonResponse({
        'id': chosen.id,
        'name': chosen.name,
        'item_id': chosen.item_id,
        'enchant': chosen.enchant,
        'rarity': chosen.rarity,
        'image_url': chosen.get_image_url()
    })


@conditional_otp_required
def roulette_page(request):
    prizes = Prize.objects.all()
    prize_data = [{
        'name': prize.name,
        'image_url': prize.get_image_url(),
        'item_id': prize.item_id,
        'enchant': prize.enchant,
        'rarity': prize.rarity
    } for prize in prizes]

    total_spins = SpinHistory.objects.filter(user=request.user).count()
    fichas = request.user.fichas
    last_spin = SpinHistory.objects.filter(user=request.user).order_by('-created_at').first()

    return render(request, 'roulette/spin.html', {
        'prizes': prize_data,
        'fichas': fichas,
        'total_spins': total_spins,
        'last_spin': last_spin,
    })


@conditional_otp_required
def comprar_fichas(request):
    if request.method == 'POST':
        quantidade = int(request.POST.get('quantidade', 0))
        valor_unitario = Decimal('0.10')  # 10 centavos por ficha
        total = valor_unitario * quantidade

        wallet = Wallet.objects.get(usuario=request.user)

        try:
            aplicar_transacao(
                wallet=wallet,
                tipo='SAIDA',
                valor=total,
                descricao=f'{quantidade} ficha(s) comprada(s)',
                origem='Wallet',
                destino='Sistema de Fichas'
            )
            # Credita as fichas
            request.user.fichas += quantidade
            request.user.save()
            return JsonResponse({'success': True, 'fichas': request.user.fichas})
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)


@conditional_otp_required
def box_dashboard_view(request):
    box_types = BoxType.objects.all()
    wallet = Wallet.objects.filter(usuario=request.user).first()

    # Caixas do usuário com boosters restantes
    user_boxes = (
        Box.objects.filter(user=request.user)
        .annotate(remaining_boosters=Count('items', filter=Q(items__opened=False)))
        .filter(remaining_boosters__gt=0)
    )

    # Cria um dicionário com o ID do tipo da caixa como chave
    box_map = {box.box_type.id: box for box in user_boxes}

    return render(request, 'box/dashboard.html', {
        'box_types': box_types,
        'user_balance': wallet.saldo if wallet else 0,
        'user_boxes': box_map
    })


@conditional_otp_required
def box_opening_home(request):
    boxes = Box.objects.filter(user=request.user).order_by('-id')
    return render(request, 'box/opening_home.html', {'boxes': boxes})


@conditional_otp_required
def open_box_view(request, box_id):
    try:
        box = Box.objects.get(id=box_id)
    except Box.DoesNotExist:
        messages.warning(request, _("Esta caixa não existe. Você pode comprá-la abaixo."))
        return redirect('games:box_user_dashboard')  # Dashboard com todas as BoxType

    if box.user != request.user:
        messages.warning(request, _("Essa caixa não pertence a você. Compre uma nova do mesmo tipo."))
        return redirect('games:box_user_dashboard')

    # Verificar se o usuário possui fichas suficientes
    if request.user.fichas <= 0:
        messages.warning(request, _("Você não tem fichas suficientes para abrir a caixa."))
        return redirect('games:box_user_dashboard')

    # Deduzir uma ficha do saldo
    request.user.fichas -= 1
    request.user.save()

    # Abrir a caixa
    item, error = open_box(request.user, box_id)

    if error:
        messages.warning(request, error)
        return redirect('games:box_user_dashboard')

    return render(request, 'box/result.html', {'item': item})


@conditional_otp_required
def buy_and_open_box_view(request, box_type_id):
    try:
        box_type = BoxType.objects.get(id=box_type_id)
    except BoxType.DoesNotExist:
        messages.error(request, _("Tipo de caixa não encontrado."))
        return redirect('games:box_user_dashboard')

    # Verificar se há itens cadastrados no banco de dados
    if not Item.objects.exists():
        messages.error(request, _("Não há itens cadastrados para abrir caixas."))
        return redirect('games:box_user_dashboard')

    # Verificar se o tipo de caixa tem itens disponíveis para a raridade que ele define
    if not box_type.boosters_amount:
        messages.error(request, _("Essa caixa não contém itens disponíveis para a abertura."))
        return redirect('games:box_user_dashboard')

    # Verificar se o usuário tem saldo suficiente para comprar a caixa
    total = box_type.price  # O preço da caixa é definido no modelo BoxType

    wallet = Wallet.objects.get(usuario=request.user)

    if wallet.saldo < total:
        messages.error(request, _("Saldo insuficiente para comprar a caixa."))
        return redirect('games:box_user_dashboard')

    # Aplicar a transação de saída da carteira para o sistema de caixas
    try:
        aplicar_transacao(
            wallet=wallet,
            tipo='SAIDA',
            valor=total,
            descricao=f'Compra de caixa {box_type.name}',
            origem='Wallet',
            destino='Sistema de Caixas'
        )
        # Criar a caixa e preencher com itens
        box = Box.objects.create(user=request.user, box_type=box_type)
        populate_box_with_items(box)
        return redirect('games:box_user_open_box', box_id=box.id)

    except ValueError as e:
        messages.error(request, _("Erro na transação: ") + str(e))
        return redirect('games:box_user_dashboard')


@conditional_otp_required
def bag_dashboard(request):
    try:
        bag = request.user.bag
        bag_items = bag.items.all()
    except Bag.DoesNotExist:
        bag = None
        bag_items = []

    personagens = Inventory.objects.filter(user=request.user).values_list('character_name', flat=True)

    return render(request, 'pages/bag_dashboard.html', {
        'bag': bag,
        'items': bag_items,
        'personagens': personagens,
    })


@conditional_otp_required
@transaction.atomic
def transferir_item_bag(request):
    if request.method == 'POST':
        item_id = parse_int(request.POST.get('item_id'))
        enchant = parse_int(request.POST.get('enchant'))
        quantity = parse_int(request.POST.get('quantity'))
        character_name_destino = request.POST.get('character_name_destino')

        bag = request.user.bag
        try:
            bag_item = BagItem.objects.get(bag=bag, item_id=item_id, enchant=enchant)
            if bag_item.quantity < quantity:
                messages.error(request, _('Quantidade insuficiente na Bag.'))
                return redirect('games:bag_dashboard')

            inventario_destino = get_object_or_404(Inventory, character_name=character_name_destino)

            # Remover da Bag
            bag_item.quantity -= quantity
            if bag_item.quantity == 0:
                bag_item.delete()
            else:
                bag_item.save()

            # Adicionar ao Inventário
            inventory_item, created = InventoryItem.objects.get_or_create(
                inventory=inventario_destino,
                item_id=item_id,
                enchant=enchant,
                defaults={'item_name': bag_item.item_name, 'quantity': quantity}
            )
            if not created:
                inventory_item.quantity += quantity
                inventory_item.save()

            # Log opcional
            InventoryLog.objects.create(
                user=request.user,
                inventory=inventario_destino,
                item_id=item_id,
                item_name=bag_item.item_name,
                enchant=enchant,
                quantity=quantity,
                acao='BAG_PARA_INVENTARIO',
                origem='BAG',
                destino=character_name_destino
            )

            messages.success(request, _('Item transferido com sucesso.'))
        except BagItem.DoesNotExist:
            messages.error(request, _('Item não encontrado na Bag.'))
        return redirect('games:bag_dashboard')


@conditional_otp_required
@transaction.atomic
def esvaziar_bag_para_inventario(request):
    if request.method == 'POST':
        character_name_destino = request.POST.get('character_name_destino')
        inventario_destino = get_object_or_404(Inventory, character_name=character_name_destino)
        bag = request.user.bag

        for bag_item in bag.items.all():
            inventory_item, created = InventoryItem.objects.get_or_create(
                inventory=inventario_destino,
                item_id=bag_item.item_id,
                enchant=bag_item.enchant,
                defaults={'item_name': bag_item.item_name, 'quantity': bag_item.quantity}
            )
            if not created:
                inventory_item.quantity += bag_item.quantity
                inventory_item.save()

            InventoryLog.objects.create(
                user=request.user,
                inventory=inventario_destino,
                item_id=bag_item.item_id,
                item_name=bag_item.item_name,
                enchant=bag_item.enchant,
                quantity=bag_item.quantity,
                acao='BAG_PARA_INVENTARIO',
                origem='BAG',
                destino=character_name_destino
            )

        bag.items.all().delete()
        messages.success(request, _('Todos os itens foram transferidos para o inventário.'))
        return redirect('games:bag_dashboard')
