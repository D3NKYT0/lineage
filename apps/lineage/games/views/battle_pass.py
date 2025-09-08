from django.shortcuts import render
from ..models import UserBattlePassProgress, BattlePassSeason, BattlePassReward, BattlePassItemExchange, Bag, BagItem, BattlePassLevel
from apps.main.home.decorator import conditional_otp_required
from django.shortcuts import redirect, get_object_or_404
from apps.lineage.wallet.models import Wallet
from apps.lineage.wallet.signals import aplicar_transacao
from django.contrib import messages
from django.utils.translation import gettext_lazy as gettext


@conditional_otp_required
def battle_pass_view(request):
    season = BattlePassSeason.objects.filter(is_active=True).first()

    if not season:
        return render(request, 'battlepass/no_active_season.html')  # crie este template para dar feedback ao usuário

    progress, created = UserBattlePassProgress.objects.get_or_create(
        user=request.user,
        season=season
    )

    # Obtém o nível atual e o próximo nível
    current_level = progress.get_current_level()
    if current_level is None:
        current_level_number = 0
    else:
        current_level_number = current_level.level

    next_level = BattlePassLevel.objects.filter(
        season=season,
        level__gt=current_level_number
    ).order_by('level').first()

    # Calcula o progresso para o próximo nível
    if next_level:
        if current_level_number == 0:
            current_level_xp = 0
        else:
            current_level_xp = BattlePassLevel.objects.get(
                season=season,
                level=current_level_number
            ).required_xp
        xp_for_next_level = next_level.required_xp - current_level_xp
        current_xp = progress.xp - current_level_xp
        progress_percentage = min(100, int((current_xp / xp_for_next_level) * 100))
    else:
        xp_for_next_level = 0
        current_xp = 0
        progress_percentage = 100

    levels = season.battlepasslevel_set.order_by('level').prefetch_related('battlepassreward_set')
    return render(request, 'battlepass/battle_pass.html', {
        'season': season,
        'progress': progress,
        'levels': levels,
        'current_level': current_level_number,
        'next_level': next_level.level if next_level else None,
        'current_xp': current_xp,
        'xp_for_next_level': xp_for_next_level,
        'progress_percentage': progress_percentage,
    })


@conditional_otp_required
def claim_reward(request, reward_id):
    reward = get_object_or_404(BattlePassReward, id=reward_id)
    progress = get_object_or_404(UserBattlePassProgress, user=request.user, season=reward.level.season)

    current_level = progress.get_current_level()
    current_level_number = current_level.level if current_level is not None else 0

    if reward.level.level <= current_level_number:
        if not reward.is_premium or progress.has_premium:
            if reward not in progress.claimed_rewards.all():
                # Adiciona o item à bag do usuário
                bag_item = reward.add_to_user_bag(request.user)
                if bag_item:
                    messages.success(request, gettext("Recompensa resgatada com sucesso!"))
                else:
                    messages.warning(request, gettext("Recompensa resgatada, mas não há item associado."))
                progress.claimed_rewards.add(reward)
            else:
                messages.info(request, gettext("Você já resgatou esta recompensa."))
        else:
            messages.error(request, gettext("Você precisa do Passe Premium para resgatar esta recompensa."))
    else:
        messages.error(request, gettext("Você ainda não atingiu o nível necessário para esta recompensa."))

    return redirect('games:battle_pass')


@conditional_otp_required
def buy_battle_pass_premium_view(request):
    season = BattlePassSeason.objects.filter(is_active=True).first()

    if not season:
        messages.error(request, gettext("Nenhuma temporada ativa no momento."))
        return redirect('games:battle_pass')

    progress, created = UserBattlePassProgress.objects.get_or_create(user=request.user, season=season)

    if progress.has_premium:
        messages.info(request, gettext("Você já possui o Passe de Batalha Premium."))
        return redirect('games:battle_pass')

    PREMIUM_PRICE = season.premium_price

    try:
        wallet = Wallet.objects.get(usuario=request.user)
    except Wallet.DoesNotExist:
        messages.error(request, gettext("Carteira não encontrada."))
        return redirect('games:battle_pass')

    if request.method == 'POST':
        # Confirmação da compra
        if wallet.saldo < PREMIUM_PRICE:
            messages.error(request, gettext("Saldo insuficiente para adquirir o Passe Premium."))
            return redirect('games:battle_pass')

        try:
            aplicar_transacao(
                wallet=wallet,
                tipo='SAIDA',
                valor=PREMIUM_PRICE,
                descricao=f'Compra do Battle Pass Premium - {season.name}',
                origem='Wallet',
                destino='Sistema de Battle Pass'
            )
            progress.has_premium = True
            progress.save()
            messages.success(request, gettext("Passe de Batalha Premium ativado com sucesso!"))
            return redirect('games:battle_pass')
        except ValueError as e:
            messages.error(request, gettext("Erro na transação: ") + str(e))
            return redirect('games:battle_pass')

    # GET: Mostrar tela de confirmação
    return render(request, 'battlepass/confirm_premium_purchase.html', {
        'season': season,
        'premium_price': PREMIUM_PRICE,
        'wallet': wallet
    })


@conditional_otp_required
def exchange_items_view(request):
    season = BattlePassSeason.objects.filter(is_active=True).first()
    if not season:
        messages.error(request, gettext("Não há temporada ativa no momento."))
        return redirect('games:battle_pass')

    progress = UserBattlePassProgress.objects.get(user=request.user, season=season)
    exchanges = BattlePassItemExchange.objects.filter(is_active=True)

    # Obtém o nível atual e o próximo nível
    current_level = progress.get_current_level()
    if current_level is None:
        current_level_number = 0
    else:
        current_level_number = current_level.level

    next_level = BattlePassLevel.objects.filter(
        season=season,
        level__gt=current_level_number
    ).order_by('level').first()

    # Calcula o progresso para o próximo nível
    if next_level:
        if current_level_number == 0:
            current_level_xp = 0
        else:
            current_level_xp = BattlePassLevel.objects.get(
                season=season,
                level=current_level_number
            ).required_xp
        xp_for_next_level = next_level.required_xp - current_level_xp
        current_xp = progress.xp - current_level_xp
        progress_percentage = min(100, int((current_xp / xp_for_next_level) * 100))
    else:
        xp_for_next_level = 0
        current_xp = 0
        progress_percentage = 100

    # Verifica quais itens o usuário possui
    try:
        bag = Bag.objects.get(user=request.user)
        user_items = BagItem.objects.filter(bag=bag)
        item_ids = set(user_items.values_list('item_id', 'enchant'))
        
        for exchange in exchanges:
            exchange.has_item = (exchange.item_id, exchange.item_enchant) in item_ids
            if exchange.has_item:
                exchange.item_quantity = user_items.get(
                    item_id=exchange.item_id,
                    enchant=exchange.item_enchant
                ).quantity
    except Bag.DoesNotExist:
        for exchange in exchanges:
            exchange.has_item = False

    return render(request, 'battlepass/exchange_items.html', {
        'exchanges': exchanges,
        'progress': progress,
        'current_level': current_level_number,
        'next_level': next_level.level if next_level else None,
        'current_xp': current_xp,
        'xp_for_next_level': xp_for_next_level,
        'progress_percentage': progress_percentage,
    })


@conditional_otp_required
def exchange_item(request, exchange_id):
    exchange = get_object_or_404(BattlePassItemExchange, id=exchange_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            messages.error(request, gettext("Quantidade inválida."))
            return redirect('games:exchange_items')
            
        success, message = exchange.exchange(request.user, quantity)
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    
    return redirect('games:exchange_items')
