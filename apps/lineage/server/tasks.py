from celery import shared_task


@shared_task
def verificar_cupons_expirados():
    from apps.lineage.shop.models import PromotionCode
    from django.utils import timezone

    agora = timezone.now()
    cupons_expirados = PromotionCode.objects.filter(ativo=True, validade__lt=agora)

    for cupom in cupons_expirados:
        cupom.ativo = False
        cupom.save()

        # Atualiza o status do apoiador se o cupom tiver expirado
        apoiador = cupom.apoiador
        if apoiador and apoiador.status == 'aprovado':
            apoiador.status = 'expirado'
            apoiador.save()
