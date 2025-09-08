from django.shortcuts import get_object_or_404, redirect, render
from apps.main.home.decorator import conditional_otp_required
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _

from django.db.models import Sum
from .utils.items import get_itens_json

from apps.main.home.models import PerfilGamer

from .models import Inventory, InventoryItem, BlockedServerItem, InventoryLog
from apps.lineage.server.database import LineageDB
from utils.dynamic_import import get_query_class
from django.core.paginator import Paginator
from django.http import JsonResponse
from .templatetags.itens_extras import item_image_url
from apps.lineage.games.models import Bag, BagItem

TransferFromWalletToChar = get_query_class("TransferFromWalletToChar")
TransferFromCharToWallet = get_query_class("TransferFromCharToWallet")
LineageServices = get_query_class("LineageServices")
LineageAccount = get_query_class("LineageAccount")


@conditional_otp_required
def retirar_item_servidor(request):
    db = LineageDB()
    if not db.is_connected():
        messages.error(request, 'O banco do jogo está indisponível no momento. Tente novamente mais tarde.')
        return redirect('inventory:inventario_dashboard')
    
    # Verifica se a conta Lineage está vinculada
    account_data = LineageAccount.check_login_exists(request.user.username)
    if not account_data or len(account_data) == 0:
        return redirect('server:lineage_register')
    
    if not account_data[0].get("linked_uuid"):
        messages.error(request, "Sua conta Lineage não está vinculada. Por favor, vincule sua conta antes de atualizar a senha.")
        return redirect('server:link_lineage_account')
    
    user_uuid = str(request.user.uuid)
    if account_data[0].get("linked_uuid") != user_uuid:
        messages.error(request, "Sua conta Lineage está vinculada a outro usuário. Por favor, vincule novamente sua conta corretamente.")
        return redirect('server:link_lineage_account')

    personagens = []
    try:
        personagens = LineageServices.find_chars(request.user.username)
    except:
        messages.warning(request, 'Não foi possível carregar seus personagens agora.')

    char_id = request.GET.get('char_id') or request.POST.get('char_id')
    page_number = request.GET.get('page')
    items = []
    personagem = None

    if char_id:
        try:
            personagem = TransferFromCharToWallet.find_char(request.user.username, char_id)
            if not personagem:
                messages.error(request, 'Personagem não encontrado ou não pertence à sua conta.')
                return redirect('inventory:retirar_item')

            if personagem[0]['online'] != 0:
                messages.error(request, 'O personagem precisa estar offline.')
                return redirect('inventory:retirar_item')

            all_items = TransferFromCharToWallet.list_items(char_id)
            itens_data = get_itens_json()

            # Substitui item_id pelo item_name
            for item in all_items:
                item_id_str = str(item['item_type'])
                item_name = itens_data.get(item_id_str, [f"(não identificado - {item_id_str})"])[0]
                item['name'] = item_name

            paginator = Paginator(all_items, 10)  # 10 itens por página
            items = paginator.get_page(page_number)

        except Exception as e:
            messages.error(request, f'Erro ao buscar o inventário: {str(e)}')

    if request.method == 'POST' and char_id:
        item_id = int(request.POST.get('item_id').replace(',', '').replace('.', ''))
        quantity = int(request.POST.get('quantity').replace(',', '').replace('.', ''))
        senha = request.POST.get('senha')

        user = authenticate(username=request.user.username, password=senha)
        if not user:
            messages.error(request, 'Senha incorreta.')
            return redirect(f"{request.path}?char_id={char_id}")

        # --- Validação: Item Bloqueado? ---
        blocked_item = BlockedServerItem.objects.filter(item_id=item_id).first()
        if blocked_item:
            reason_text = f" Motivo: {blocked_item.reason}." if blocked_item.reason else ""
            messages.error(request, f'O item selecionado não pode ser retirado do servidor.{reason_text}')
            return redirect(f"{request.path}?char_id={char_id}")
        # -----------------------------------

        if not items:
            messages.error(request, 'Inventário não carregado.')
            return redirect('inventory:retirar_item')

        item_status = TransferFromCharToWallet.check_ingame_coin(item_id, char_id)
        if item_status['total'] < quantity:
            messages.error(request, 'Quantidade insuficiente no jogo.')
            return redirect(f"{request.path}?char_id={char_id}")

        success = TransferFromCharToWallet.remove_ingame_coin(item_id, quantity, char_id)
        if not success:
            messages.error(request, 'Falha ao remover o item do jogo.')
            return redirect(f"{request.path}?char_id={char_id}")
        
        # Localiza ou cria o inventário online do personagem
        inventory, created = Inventory.objects.get_or_create(
            user=request.user,
            account_name=request.user.username,
            character_name=personagem[0]['char_name'],
        )

        # Verifica se já existe esse item no inventário
        inventory_item, created = InventoryItem.objects.get_or_create(
            inventory=inventory,
            item_id=item_id,
            enchant=item_status['enchant'],
            defaults={'item_name': itens_data.get(str(item_id), [f"(não identificado - {str(item_id)})"])[0], 'quantity': 0}
        )

        # Atualiza a quantidade
        inventory_item.quantity += quantity
        inventory_item.save()

        # Registrar o log
        InventoryLog.objects.create(
            user=request.user,
            inventory=inventory,
            item_id=item_id,
            item_name=inventory_item.item_name,
            enchant=inventory_item.enchant,
            quantity=quantity,
            acao='RETIROU_DO_JOGO',
            origem=personagem[0]['char_name'],
            destino='Inventário Online'
        )

        messages.success(request, 'Item transferido com sucesso!')
        return redirect(f"{request.path}?char_id={char_id}")

    return render(request, 'pages/retirar_item.html', {
        'personagens': personagens,
        'char_id': char_id,
        'items': items,
        'personagem': personagem[0] if personagem else None
    })


@conditional_otp_required
def inserir_item_servidor(request, char_name, item_id):
    db = LineageDB()
    if not db.is_connected():
        messages.error(request, 'O banco do jogo está indisponível no momento. Tente novamente mais tarde.')
        return redirect('inventory:inventario_dashboard')

    try:
        personagem = TransferFromWalletToChar.find_char(request.user.username, char_name)
        if not personagem:
            messages.error(request, 'Personagem não encontrado ou não pertence à sua conta.')
            return redirect('inventory:inventario_dashboard')

    except Exception as e:
        messages.error(request, f'Erro ao buscar personagem: {str(e)}')
        return redirect('inventory:inventario_dashboard')

    try:
        inventory = Inventory.objects.get(
            user=request.user,
            account_name=request.user.username,
            character_name=personagem[0]['char_name']
        )
        item = InventoryItem.objects.get(inventory=inventory, item_id=item_id)
    except InventoryItem.DoesNotExist:
        messages.error(request, 'Item não encontrado no inventário online.')
        return redirect('inventory:inventario_dashboard')

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity').replace(',', '').replace('.', ''))
        senha = request.POST.get('senha')

        user = authenticate(username=request.user.username, password=senha)
        if not user:
            messages.error(request, 'Senha incorreta.')
            return redirect(request.path)

        if item.quantity < quantity:
            messages.error(request, 'Quantidade insuficiente no inventário.')
            return redirect(request.path)
        
        if not TransferFromWalletToChar.items_delayed:
            if personagem[0]['online'] != 0:
                messages.error(request, 'O personagem precisa estar offline.')
                return redirect(request.path)

        success = TransferFromWalletToChar.insert_coin(personagem[0]['char_name'], item_id, quantity, item.enchant)
        if not success:
            messages.error(request, 'Falha ao inserir o item no servidor.')
            return redirect(request.path)

        item.quantity -= quantity

        if item.quantity == 0:
            item.delete()
        else:
            item.save()

        # Registrar o log de inserção
        InventoryLog.objects.create(
            user=request.user,
            inventory=inventory,
            item_id=item_id,
            item_name=item.item_name,
            enchant=item.enchant,
            quantity=quantity,
            acao='INSERIU_NO_JOGO',
            origem='Inventário Online',
            destino=personagem[0]['char_name']
        )

        messages.success(request, f'{quantity}x {item.item_name} inserido no servidor com sucesso!')
        return redirect('inventory:inventario_dashboard')

    return render(request, 'pages/inserir_item_direct.html', {
        'personagem': personagem[0],
        'item': item,
    })


@conditional_otp_required
@transaction.atomic
def trocar_item_com_jogador(request):
    if request.method == 'POST':
        character_name_origem = request.POST.get('character_name_origem')
        character_name_destino = request.POST.get('character_name_destino')
        item_id = int(request.POST.get('item_id').replace(',', '').replace('.', ''))
        quantity = int(request.POST.get('quantity').replace(',', '').replace('.', ''))

        inventario_origem = get_object_or_404(Inventory, character_name=character_name_origem, user=request.user)
        inventario_destino = get_object_or_404(Inventory, character_name=character_name_destino)

        try:
            item_origem = InventoryItem.objects.get(inventory=inventario_origem, item_id=item_id)
            if item_origem.quantity < quantity:
                messages.error(request, 'Quantidade insuficiente para troca.')
                return redirect('inventory:trocar_item')

            item_origem.quantity -= quantity
            if item_origem.quantity == 0:
                item_origem.delete()
            else:
                item_origem.save()

            item_destino, created = InventoryItem.objects.get_or_create(
                inventory=inventario_destino,
                item_id=item_id,
                defaults={'item_name': item_origem.item_name, 'quantity': quantity}
            )
            if not created:
                item_destino.quantity += quantity
                item_destino.save()

            # Registrar o log de troca
            InventoryLog.objects.create(
                user=request.user,
                inventory=inventario_origem,
                item_id=item_id,
                item_name=item_origem.item_name,
                enchant=item_origem.enchant,
                quantity=quantity,
                acao='TROCA_ENTRE_PERSONAGENS',
                origem=character_name_origem,
                destino=character_name_destino
            )

            messages.success(request, 'Troca realizada com sucesso!')
            return redirect('inventory:inventario_dashboard')

        except InventoryItem.DoesNotExist:
            messages.error(request, 'Item não encontrado no inventário de origem.')
            return redirect('inventory:trocar_item')

        except Exception as e:
            messages.error(request, f'Erro: {str(e)}')
            return redirect('inventory:trocar_item')

    # --- GET (preenche o form com os dados da querystring) ---
    character_name_origem = request.GET.get('character_name_origem', '')
    item_id = int(request.GET.get('item_id').replace(',', '').replace('.', ''))

    item_name = ''
    max_quantity = 0

    if character_name_origem and item_id:
        try:
            inventario = Inventory.objects.get(character_name=character_name_origem, user=request.user)
            item = InventoryItem.objects.get(inventory=inventario, item_id=item_id)
            item_name = item.item_name
            max_quantity = item.quantity
        except (Inventory.DoesNotExist, InventoryItem.DoesNotExist):
            messages.error(request, 'Item ou inventário não encontrado.')

    context = {
        'character_name_origem': character_name_origem,
        'item_id': item_id,
        'item_name': item_name,
        'max_quantity': max_quantity
    }
    return render(request, 'pages/trocar_item.html', context)


@conditional_otp_required
def inventario_dashboard(request):
    # Obter personagens da conta do usuário
    try:
        personagens = LineageServices.find_chars(request.user.username)
        personagens_nomes = [p['char_name'] for p in personagens]
    except Exception as e:
        messages.error(request, 'Erro ao carregar personagens da conta. Tente novamente.')
        personagens_nomes = []
        personagens = []

    # Obter inventários existentes
    inventories = Inventory.objects.filter(user=request.user)
    inventarios_existentes = {inv.character_name: inv for inv in inventories}
    
    # Lista para armazenar inventários obsoletos
    inventarios_obsoletos = []
    
    # Criar inventários para personagens que não têm
    inventarios_criados = []
    for personagem in personagens_nomes:
        if personagem not in inventarios_existentes:
            try:
                inventory = Inventory.objects.create(
                    user=request.user,
                    account_name=request.user.username,
                    character_name=personagem
                )
                inventarios_criados.append(personagem)
            except Exception as e:
                messages.error(request, f'Erro ao criar inventário para {personagem}: {str(e)}')
    
    # Verificar inventários obsoletos (personagens que não existem mais na conta)
    for inv in inventories:
        if inv.character_name not in personagens_nomes:
            inventarios_obsoletos.append(inv.character_name)
    
    # Mostrar mensagens informativas
    if inventarios_criados:
        if len(inventarios_criados) == 1:
            messages.success(request, f"{_('Inventário criado para o personagem')} {inventarios_criados[0]}.")
        else:
            messages.success(request, f"{_('Inventários criados para')} {len(inventarios_criados)} {_('personagens.')}")
    
    if inventarios_obsoletos:
        if len(inventarios_obsoletos) == 1:
            messages.warning(request, f"{_('Inventário obsoleto encontrado para o personagem')} {inventarios_obsoletos[0]} ({_('não existe mais na conta.')})")
        else:
            messages.warning(request, f"{_('Inventários obsoletos encontrados para')} {len(inventarios_obsoletos)} {_('personagens (não existem mais na conta).')}")
    
    # Recarregar inventários após as modificações
    inventories = Inventory.objects.filter(user=request.user)
    inventory_data = []

    for inv in inventories:
        inv.is_online = False  # ou use TransferFromCharToWallet pra pegar status real
        inv_items = InventoryItem.objects.filter(inventory=inv)
        inventory_data.append({
            'inventory': inv,
            'items': inv_items
        })

    return render(request, 'pages/inventario_dashboard.html', {
        'inventory_data': inventory_data,
        'inventarios_obsoletos': inventarios_obsoletos
    })


@conditional_otp_required
def inventario_global(request):
    # Agrupar os itens de todos os inventários do usuário e somar as quantidades
    itens_globais = InventoryItem.objects.filter(inventory__user=request.user) \
        .values('item_id', 'item_name') \
        .annotate(total_quantity=Sum('quantity')) \
        .order_by('-total_quantity')

    return render(request, 'pages/inventario_global.html', {
        'itens_globais': itens_globais
    })


@conditional_otp_required
def get_item_image_url(request, item_id):
    url = item_image_url(item_id)
    return JsonResponse({'url': url})


@conditional_otp_required
@transaction.atomic
def transferir_para_bag(request, char_name, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity').replace(',', '').replace('.', ''))
        
        try:
            # Obtém o inventário e o item
            inventory = get_object_or_404(Inventory, character_name=char_name, user=request.user)
            inventory_item = get_object_or_404(InventoryItem, inventory=inventory, item_id=item_id)
            
            if inventory_item.quantity < quantity:
                messages.error(request, 'Quantidade insuficiente no inventário.')
                return redirect(request.path)

            # Obtém ou cria a bag do usuário
            bag, created = Bag.objects.get_or_create(user=request.user)
            
            # Adiciona o item à bag
            bag_item, created = BagItem.objects.get_or_create(
                bag=bag,
                item_id=item_id,
                enchant=inventory_item.enchant,
                defaults={
                    'item_name': inventory_item.item_name,
                    'quantity': quantity
                }
            )
            
            if not created:
                bag_item.quantity += quantity
                bag_item.save()

            # Atualiza a quantidade no inventário
            inventory_item.quantity -= quantity
            if inventory_item.quantity == 0:
                inventory_item.delete()
            else:
                inventory_item.save()

            # Registra o log
            InventoryLog.objects.create(
                user=request.user,
                inventory=inventory,
                item_id=item_id,
                item_name=inventory_item.item_name,
                enchant=inventory_item.enchant,
                quantity=quantity,
                acao='BAG_PARA_INVENTARIO',
                origem=char_name,
                destino='Bag'
            )

            messages.success(request, f'{quantity}x {inventory_item.item_name} transferido para a bag com sucesso!')
            return redirect('inventory:inventario_dashboard')

        except Exception as e:
            messages.error(request, f'Erro ao transferir item: {str(e)}')
            return redirect('inventory:inventario_dashboard')

    # GET: Mostra o formulário
    try:
        inventory = get_object_or_404(Inventory, character_name=char_name, user=request.user)
        item = get_object_or_404(InventoryItem, inventory=inventory, item_id=item_id)
        
        return render(request, 'pages/transferir_para_bag.html', {
            'inventory': inventory,
            'item': item
        })
    except Exception as e:
        messages.error(request, f'Erro ao carregar item: {str(e)}')
        return redirect('inventory:inventario_dashboard')


@conditional_otp_required
@transaction.atomic
def deletar_inventario_obsoleto(request, character_name):
    """
    Deleta um inventário obsoleto, transferindo seus itens para a bag se necessário
    """
    try:
        # Verificar se o inventário existe e pertence ao usuário
        inventory = get_object_or_404(Inventory, character_name=character_name, user=request.user)
        
        # Verificar se o personagem realmente não existe mais na conta
        try:
            personagens = LineageServices.find_chars(request.user.username)
            personagens_nomes = [p['char_name'] for p in personagens]
            
            if character_name in personagens_nomes:
                messages.error(request, _('Este personagem ainda existe na sua conta. Não é possível deletar o inventário.'))
                return redirect('inventory:inventario_dashboard')
                
        except Exception as e:
            messages.error(request, _('Erro ao verificar personagens da conta. Tente novamente.'))
            return redirect('inventory:inventario_dashboard')
        
        # Obter todos os itens do inventário
        inventory_items = InventoryItem.objects.filter(inventory=inventory)
        itens_transferidos = []
        
        if inventory_items.exists():
            # Obter ou criar a bag do usuário
            bag, created = Bag.objects.get_or_create(user=request.user)
            
            # Transferir todos os itens para a bag
            for item in inventory_items:
                bag_item, created = BagItem.objects.get_or_create(
                    bag=bag,
                    item_id=item.item_id,
                    enchant=item.enchant,
                    defaults={
                        'item_name': item.item_name,
                        'quantity': item.quantity
                    }
                )
                
                if not created:
                    bag_item.quantity += item.quantity
                    bag_item.save()
                
                itens_transferidos.append(f"{item.quantity}x {item.item_name}")
                
                # Registrar o log
                InventoryLog.objects.create(
                    user=request.user,
                    inventory=inventory,
                    item_id=item.item_id,
                    item_name=item.item_name,
                    enchant=item.enchant,
                    quantity=item.quantity,
                    acao='BAG_PARA_INVENTARIO',
                    origem=character_name,
                    destino='Bag'
                )
            
            # Deletar todos os itens do inventário
            inventory_items.delete()
            
            # Mostrar mensagem sobre itens transferidos
            if len(itens_transferidos) == 1:
                messages.success(request, f"{_('Inventário obsoleto deletado. Item transferido para a bag:')} {itens_transferidos[0]}")
            else:
                messages.success(request, f"{_('Inventário obsoleto deletado.')} {len(itens_transferidos)} {_('itens transferidos para a bag.')}")
        else:
            messages.success(request, f"{_('Inventário obsoleto deletado.')} {_('Nenhum item encontrado.')}")
        
        # Deletar o inventário
        inventory.delete()
        
        return redirect('inventory:inventario_dashboard')
        
    except Inventory.DoesNotExist:
        messages.error(request, _('Inventário não encontrado.'))
        return redirect('inventory:inventario_dashboard')
    except Exception as e:
        messages.error(request, f"{_('Erro ao deletar inventário:')} {str(e)}")
        return redirect('inventory:inventario_dashboard')
