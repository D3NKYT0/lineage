import logging

from celery import shared_task
from .models import Notification


logger = logging.getLogger(__name__)


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
