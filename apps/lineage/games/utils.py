from .models import *
from apps.main.home.models import ConquistaUsuario
from django.contrib import messages
from django.utils.translation import gettext as gettext_lazy


def entregar_item_para_bag(user, item_id, item_name, quantity=1, enchant=0, request=None):
    bag, created = Bag.objects.get_or_create(user=user)
    bag_item, created = BagItem.objects.get_or_create(
        bag=bag,
        item_id=item_id,
        enchant=enchant,
        defaults={'item_name': item_name, 'quantity': quantity}
    )
    if not created:
        bag_item.quantity += quantity
        bag_item.save()

    if request:
        messages.success(
            request,
            gettext_lazy("🎁 Você recebeu: {item} +{enchant} x{qty}!").format(
                item=item_name,
                enchant=enchant,
                qty=quantity
            )
        )


def recompensa_ja_recebida(user, recompensa):
    return RecompensaRecebida.objects.filter(user=user, recompensa=recompensa).exists()


def registrar_recompensa_recebida(user, recompensa):
    RecompensaRecebida.objects.create(user=user, recompensa=recompensa)


def verificar_recompensas_por_nivel(user, level, request=None):
    recompensas = Recompensa.objects.filter(tipo__iexact='NIVEL')

    for recompensa in recompensas:
        try:
            nivel_recompensa = int(recompensa.referencia)
        except (ValueError, TypeError):
            continue

        if nivel_recompensa <= level and not recompensa_ja_recebida(user, recompensa):
            entregar_item_para_bag(
                user,
                item_id=recompensa.item_id,
                item_name=recompensa.item_name,
                quantity=recompensa.quantity,
                enchant=recompensa.enchant,
                request=request
            )
            registrar_recompensa_recebida(user, recompensa)


def verificar_recompensas_por_conquista(user, codigo_conquista, request=None):
    if not ConquistaUsuario.objects.filter(usuario=user, conquista__codigo=codigo_conquista).exists():
        return

    recompensas_recebidas_ids = set(
        RecompensaRecebida.objects.filter(user=user).values_list('recompensa_id', flat=True)
    )

    recompensas = Recompensa.objects.filter(tipo='CONQUISTA', referencia=codigo_conquista)

    for recompensa in recompensas:
        if recompensa.id not in recompensas_recebidas_ids:
            entregar_item_para_bag(
                user,
                item_id=recompensa.item_id,
                item_name=recompensa.item_name,
                quantity=recompensa.quantity,
                enchant=recompensa.enchant,
                request=request
            )
            registrar_recompensa_recebida(user, recompensa)

    total_conquistas = ConquistaUsuario.objects.filter(usuario=user).count()
    recompensas_qtd = Recompensa.objects.filter(tipo='CONQUISTAS_MULTIPLAS')

    for recompensa in recompensas_qtd:
        try:
            numero_conquistas_referencia = int(recompensa.referencia)
        except (ValueError, TypeError):
            continue

        if total_conquistas >= numero_conquistas_referencia and recompensa.id not in recompensas_recebidas_ids:
            entregar_item_para_bag(
                user,
                item_id=recompensa.item_id,
                item_name=recompensa.item_name,
                quantity=recompensa.quantity,
                enchant=recompensa.enchant,
                request=request
            )
            registrar_recompensa_recebida(user, recompensa)
