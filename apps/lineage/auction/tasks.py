from celery import shared_task
import logging
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


@shared_task
def encerrar_leiloes_expirados():
    from .services import finish_auction
    from .models import Auction
    from django.utils.timezone import now

    expirados = Auction.objects.filter(end_time__lte=now())
    count = expirados.count()

    for leilao in expirados:
        try:
            if leilao.is_active():
                finish_auction(leilao)
        except Exception as e:
            logger.error(_('Erro ao encerrar leilão %(id)s: %(erro)s') % {
                'id': leilao.id,
                'erro': str(e)
            })

    logger.info(_('%(qtd)d leilões encerrados automaticamente.') % {'qtd': count})
