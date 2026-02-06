import logging

from celery import shared_task
from django.conf import settings
from .models import Notification


logger = logging.getLogger(__name__)


def execute_task_sync_or_async(task_func, *args, **kwargs):
    """
    Helper que executa task de forma síncrona em DEBUG ou assíncrona em produção.
    Útil para tasks que não são do Beat (agendadas).
    
    Em DEBUG: executa síncronamente usando .apply() para manter contexto do Celery
    Em produção: executa assincronamente usando .delay()
    """
    if settings.DEBUG:
        # Em DEBUG, executa síncronamente mas mantém contexto do Celery
        # .apply() executa de forma síncrona mas preserva bind=True e outros recursos
        return task_func.apply(args=args, kwargs=kwargs)
    else:
        # Em produção, executa assincronamente
        return task_func.delay(*args, **kwargs)


@shared_task
def create_notification(user_id, is_system, message):
    try:
        notification_type = Notification.SYSTEM if is_system else Notification.USER
        
        # Criação da notificação
        notification = Notification.objects.create(
            user_id=user_id if not is_system else None,
            notification_type=notification_type,
            message=message,
            viewed=False,  # Por padrão, a notificação não foi visualizada
        )
        
        return notification.id  # Retorna o ID da nova notificação
    except Exception as e:
        logger.error(f"Erro ao criar notificação: {str(e)}")  # Registra o erro
        raise  # Opcional: Re-raise a exceção para que o Celery a trate como uma falha


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def send_push_notification_async(self, user_id, title, body, url=None):
    """Envia push notification de forma assíncrona"""
    from apps.main.home.models import User
    from utils.push import send_webpush_notification
    
    try:
        # .defer('avatar') evita carregar o arquivo no worker (pode não existir no FS do container)
        user = User.objects.defer("avatar").get(id=user_id)
        send_webpush_notification(user, title, body, url)
        logger.info(f"Push notification enviada para usuário {user_id}")
        return True
    except User.DoesNotExist:
        logger.error(f"Usuário {user_id} não encontrado")
        return False
    except Exception as e:
        logger.error(f"Erro ao enviar push notification para usuário {user_id}: {e}")
        raise self.retry(exc=e, countdown=30)


@shared_task
def send_push_batch(notifications_data):
    """Envia múltiplas push notifications de uma vez"""
    sent = 0
    failed = 0
    
    for data in notifications_data:
        try:
            execute_task_sync_or_async(
                send_push_notification_async,
                user_id=data['user_id'],
                title=data.get('title', 'Notificação'),
                body=data['body'],
                url=data.get('url')
            )
            sent += 1
        except Exception as e:
            logger.error(f"Erro ao {'enviar' if settings.DEBUG else 'agendar'} push notification: {e}")
            failed += 1
    
    logger.info(f"Push notifications {'enviadas' if settings.DEBUG else 'agendadas'}: {sent} enviadas, {failed} falhas")
    return {'sent': sent, 'failed': failed}