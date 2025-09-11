from django.shortcuts import render, get_object_or_404, redirect
from apps.main.home.decorator import conditional_otp_required
from apps.main.resources.decorators import require_shop_module
from django.contrib import messages
from django.db import transaction
from django.utils.translation import gettext as _
from .models import ShopItem, ShopPackage, Cart, CartItem, CartPackage, PromotionCode, ShopPurchase, PurchaseItem
from apps.lineage.wallet.signals import aplicar_transacao
from apps.lineage.inventory.models import InventoryItem, Inventory
from apps.lineage.wallet.models import Wallet
from django.core.paginator import Paginator

from apps.main.home.models import PerfilGamer

from utils.dynamic_import import get_query_class
LineageServices = get_query_class("LineageServices")


@conditional_otp_required
@require_shop_module
def shop_home(request):
    item_list = ShopItem.objects.filter(ativo=True)
    package_list = ShopPackage.objects.filter(ativo=True)

    item_paginator = Paginator(item_list, 6)  # 6 por página
    package_paginator = Paginator(package_list, 6)

    item_page = request.GET.get('items_page')
    package_page = request.GET.get('packages_page')

    items = item_paginator.get_page(item_page)
    packages = package_paginator.get_page(package_page)

    return render(request, 'shop/home.html', {
        'items': items,
        'packages': packages
    })


@conditional_otp_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    wallet, created = Wallet.objects.get_or_create(usuario=request.user)
    
    # Buscar personagens do usuário
    try:
        personagens = LineageServices.find_chars(request.user.username)
    except Exception as e:
        personagens = []
        messages.warning(request, 'Erro ao carregar personagens. Tente novamente.')

    # Calcular pagamento misto se usar bônus
    valor_bonus_usado, valor_dinheiro_usado = cart.calcular_pagamento_misto(wallet.saldo_bonus)
    
    context = {
        'cart': cart,
        'personagens': personagens,
        'wallet': wallet,
        'valor_bonus_usado': valor_bonus_usado,
        'valor_dinheiro_usado': valor_dinheiro_usado,
    }
    
    return render(request, 'shop/cart.html', context)


@conditional_otp_required
def add_item_to_cart(request, item_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    item = get_object_or_404(ShopItem, id=item_id, ativo=True)
    
    quantidade = int(request.GET.get('quantidade', 1))
    
    if quantidade < 1:
        messages.error(request, "A quantidade deve ser maior que zero.")
        return redirect('shop:shop_home')
        
    if quantidade > 99:  # Limite máximo por item
        messages.error(request, "Quantidade máxima excedida.")
        return redirect('shop:shop_home')
    
    # Verificar se já existe o item no carrinho (lidando com possíveis duplicatas)
    cart_items = CartItem.objects.filter(cart=cart, item=item)
    
    if cart_items.exists():
        # Se existem múltiplos registros, pegar o primeiro e deletar os outros
        if cart_items.count() > 1:
            # Manter apenas o primeiro registro e deletar os duplicados
            first_item = cart_items.first()
            cart_items.exclude(id=first_item.id).delete()
            cart_item = first_item
        else:
            cart_item = cart_items.first()
        
        # Atualizar quantidade
        cart_item.quantidade += quantidade
        if cart_item.quantidade > 99:
            messages.error(request, "Quantidade máxima no carrinho excedida.")
            return redirect('shop:shop_home')
    else:
        # Criar novo item no carrinho
        cart_item = CartItem.objects.create(cart=cart, item=item, quantidade=quantidade)
    
    cart_item.save()
    
    messages.success(request, f"{item.nome} adicionado ao carrinho.")
    return redirect('shop:shop_home')


@conditional_otp_required
def add_package_to_cart(request, package_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    pacote = get_object_or_404(ShopPackage, id=package_id, ativo=True)
    cart_package, created = CartPackage.objects.get_or_create(cart=cart, pacote=pacote)
    if not created:
        cart_package.quantidade += 1
    cart_package.save()
    messages.success(request, f"Pacote {pacote.nome} adicionado ao carrinho.")
    return redirect('shop:shop_home')


@conditional_otp_required
def toggle_bonus_usage(request):
    """Alterna o uso de bônus no carrinho"""
    if request.method == 'POST':
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.usar_bonus = not cart.usar_bonus
        cart.save()
        
        if cart.usar_bonus:
            messages.success(request, "Pagamento com bônus ativado!")
        else:
            messages.info(request, "Pagamento apenas com dinheiro.")
    
    return redirect('shop:view_cart')


@conditional_otp_required
def apply_promo_code(request):
    if request.method == "POST":
        code = request.POST.get("promo_code")
        cart, created = Cart.objects.get_or_create(user=request.user)
        try:
            promo = PromotionCode.objects.get(codigo=code, ativo=True)
            if not promo.is_valido():
                messages.error(request, "Código expirado ou inválido.")
            else:
                cart.promocao_aplicada = promo
                cart.save()
                messages.success(request, f"Cupom {promo.codigo} aplicado!")
        except PromotionCode.DoesNotExist:
            messages.error(request, "Cupom não encontrado.")
    return redirect('shop:view_cart')


@conditional_otp_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    wallet, created = Wallet.objects.get_or_create(usuario=request.user)

    total = cart.calcular_total()
    valor_bonus_usado, valor_dinheiro_usado = cart.calcular_pagamento_misto(wallet.saldo_bonus)

    # Verificar se tem saldo suficiente
    if cart.usar_bonus:
        if wallet.saldo_bonus < valor_bonus_usado:
            messages.error(request, "Saldo de bônus insuficiente.")
            return redirect('shop:view_cart')
        if wallet.saldo < valor_dinheiro_usado:
            messages.error(request, "Saldo insuficiente na carteira.")
            return redirect('shop:view_cart')
    else:
        if wallet.saldo < total:
            messages.error(request, "Saldo insuficiente na carteira.")
            return redirect('shop:view_cart')

    personagem = request.POST.get('character_name')
    if not personagem or len(personagem.strip()) < 3:
        messages.error(request, "Informe um nome de personagem válido para entrega (mínimo 3 caracteres).")
        return redirect('shop:view_cart')

    # Verificar se o personagem existe na conta do usuário
    try:
        personagens = LineageServices.find_chars(request.user.username)
        personagem_existe = any(p['char_name'] == personagem for p in personagens)
        if not personagem_existe:
            messages.error(request, _('Este personagem não existe na sua conta.'))
            return redirect('shop:view_cart')
    except Exception as e:
        messages.error(request, 'Erro ao verificar personagens da conta. Tente novamente.')
        return redirect('shop:view_cart')

    if not cart.cartitem_set.exists() and not cart.cartpackage_set.exists():
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('shop:view_cart')

    try:
        with transaction.atomic():
            # Descontar do saldo de bônus se aplicável
            if cart.usar_bonus and valor_bonus_usado > 0:
                from apps.lineage.wallet.signals import aplicar_transacao_bonus
                aplicar_transacao_bonus(
                    wallet=wallet,
                    tipo='SAIDA',
                    valor=valor_bonus_usado,
                    descricao=f"Compra no Shop - {personagem}",
                    origem="Shop",
                    destino=personagem
                )

            # Descontar do saldo normal se aplicável
            if valor_dinheiro_usado > 0:
                aplicar_transacao(
                    wallet=wallet,
                    tipo='SAIDA',
                    valor=valor_dinheiro_usado,
                    descricao=f"Compra no Shop - {personagem}",
                    origem="Shop",
                    destino=personagem
                )

            # Enviar itens e pacotes para o inventário
            # Se o inventário não existir, será criado automaticamente
            inventory, created = Inventory.objects.get_or_create(
                user=request.user,
                account_name=request.user.username,
                character_name=personagem
            )

            # Adicionar os itens do carrinho no inventário
            for cart_item in cart.cartitem_set.all():
                quantidade_total = cart_item.quantidade * cart_item.item.quantidade

                existing_item = InventoryItem.objects.filter(
                    inventory=inventory,
                    item_id=cart_item.item.item_id
                ).first()

                if existing_item:
                    existing_item.quantity += quantidade_total
                    existing_item.save()
                else:
                    InventoryItem.objects.create(
                        inventory=inventory,
                        item_id=cart_item.item.item_id,
                        item_name=cart_item.item.nome,
                        quantity=quantidade_total
                    )

            # Adicionar os itens dos pacotes no inventário
            for cart_package in cart.cartpackage_set.all():
                for pacote_item in cart_package.pacote.shoppackageitem_set.all():
                    quantidade_total = pacote_item.quantidade * pacote_item.item.quantidade * cart_package.quantidade

                    existing_item = InventoryItem.objects.filter(
                        inventory=inventory,
                        item_id=pacote_item.item.item_id
                    ).first()

                    if existing_item:
                        existing_item.quantity += quantidade_total
                        existing_item.save()
                    else:
                        InventoryItem.objects.create(
                            inventory=inventory,
                            item_id=pacote_item.item.item_id,
                            item_name=pacote_item.item.nome,
                            quantity=quantidade_total
                        )

            # Registrar a compra
            purchase = ShopPurchase.objects.create(
                user=request.user,
                character_name=personagem,
                total_pago=total,
                valor_bonus_usado=valor_bonus_usado,
                valor_dinheiro_usado=valor_dinheiro_usado,
                promocao_aplicada=cart.promocao_aplicada
            )

            # Registrar os itens individuais da compra
            for cart_item in cart.cartitem_set.all():
                PurchaseItem.objects.create(
                    purchase=purchase,
                    item_name=cart_item.item.nome,
                    item_id=cart_item.item.item_id,
                    quantidade=cart_item.quantidade * cart_item.item.quantidade,
                    preco_unitario=cart_item.item.preco,
                    preco_total=cart_item.item.preco * cart_item.quantidade,
                    tipo_compra='item'
                )

            # Registrar os itens dos pacotes da compra
            for cart_package in cart.cartpackage_set.all():
                for pacote_item in cart_package.pacote.shoppackageitem_set.all():
                    quantidade_total = pacote_item.quantidade * pacote_item.item.quantidade * cart_package.quantidade
                    preco_unitario_pacote = cart_package.pacote.preco_total / sum(
                        pi.quantidade * pi.item.quantidade 
                        for pi in cart_package.pacote.shoppackageitem_set.all()
                    )
                    
                    PurchaseItem.objects.create(
                        purchase=purchase,
                        item_name=pacote_item.item.nome,
                        item_id=pacote_item.item.item_id,
                        quantidade=quantidade_total,
                        preco_unitario=preco_unitario_pacote,
                        preco_total=preco_unitario_pacote * quantidade_total,
                        tipo_compra='pacote',
                        nome_pacote=cart_package.pacote.nome
                    )

            # Limpar o carrinho
            cart.limpar()

            # Mensagem de sucesso
            if cart.usar_bonus and valor_bonus_usado > 0:
                messages.success(request, f"Compra realizada com sucesso! R$ {valor_bonus_usado:.2f} em bônus e R$ {valor_dinheiro_usado:.2f} em dinheiro.")
            else:
                messages.success(request, f"Compra realizada com sucesso! R$ {total:.2f} debitados da sua carteira.")

            return redirect('shop:shop_home')

    except Exception as e:
        messages.error(request, f"Erro ao processar a compra: {str(e)}")
        return redirect('shop:view_cart')


@conditional_otp_required
def purchase_history(request):
    purchases = ShopPurchase.objects.filter(user=request.user).prefetch_related('items').order_by('-data_compra')
    return render(request, 'shop/purchases.html', {'purchases': purchases})


@conditional_otp_required
def clear_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.limpar()
    messages.success(request, "Carrinho esvaziado com sucesso.")
    return redirect('shop:view_cart')


@conditional_otp_required
def remove_cart_item(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    try:
        cart_item = CartItem.objects.get(cart=cart, item_id=item_id)
        cart_item.delete()
        messages.success(request, f"{cart_item.item.nome} removido do carrinho.")
    except CartItem.DoesNotExist:
        messages.error(request, "Item não encontrado no carrinho.")
    return redirect('shop:view_cart')


@conditional_otp_required
def remove_cart_package(request, package_id):
    cart = get_object_or_404(Cart, user=request.user)
    try:
        cart_package = CartPackage.objects.get(cart=cart, pacote_id=package_id)
        cart_package.delete()
        messages.success(request, f"Pacote {cart_package.pacote.nome} removido do carrinho.")
    except CartPackage.DoesNotExist:
        messages.error(request, "Pacote não encontrado no carrinho.")
    return redirect('shop:view_cart')
