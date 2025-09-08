import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope["user"].is_anonymous:
            raise DenyConnection("User not authenticated")

        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.group_channel_name = f'chat_{self.group_name}'

        # Verifica se o usuário tem permissão para se conectar à sala do protocolo
        has_access = await self.user_has_access_to_protocol(self.scope["user"], self.group_name)

        if not has_access:
            raise DenyConnection("User does not have access to this protocol chat.")

        # Adicionar ao grupo
        await self.channel_layer.group_add(
            self.group_channel_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_channel_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']
        avatar_url = await self.get_avatar_url(sender)
        timestamp = await self.get_current_timestamp()
        saved = await self.save_message(self.group_name, sender, message)
        
        if not saved:
            await self.send(text_data=json.dumps({
                'error': 'Failed to save message.'
            }))
            return

        await self.channel_layer.group_send(
            self.group_channel_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
                'avatar_url': avatar_url,
                'timestamp': timestamp
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        avatar_url = event['avatar_url']
        timestamp = event.get('timestamp', '')

        if sender != self.scope['user'].username:
            await self.send(text_data=json.dumps({
                'message': message,
                'sender': sender,
                'avatar_url': avatar_url,
                'timestamp': timestamp
            }))

    @database_sync_to_async
    def save_message(self, group_name, sender, message):
        from apps.main.administrator.models import ChatGroup
        from apps.main.home.models import User

        try:
            sender = User.objects.get(username=sender)
            ChatGroup.objects.create(group_name=group_name, sender=sender, message=message)
        except User.DoesNotExist:
            logger.error(f"Usuário {sender} não encontrado.")
            return False
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {e}")
            return False
        return True

    @database_sync_to_async
    def get_avatar_url(self, username):
        try:
            from apps.main.home.models import User
            user = User.objects.get(username=username)
            custom_imagem = '/decrypted-file/home/user/avatar/'
            avatar_url = custom_imagem + str(user.uuid) + '/'
            return avatar_url if user.avatar else '/static/assets/img/team/generic_user.png'
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_current_timestamp(self):
        from django.utils import timezone
        return timezone.now().strftime("%d/%m/%Y, %H:%M:%S")

    @database_sync_to_async
    def user_has_access_to_protocol(self, user, protocol):
        from apps.main.solicitation.models import Solicitation
        
        try:
            # Tenta encontrar a solicitação com o protocolo correspondente
            solicitation = Solicitation.objects.get(protocol=protocol)

            # Verifica se o status é final (resolved, closed, cancelled, rejected)
            final_statuses = ['resolved', 'closed', 'cancelled', 'rejected']
            if solicitation.status in final_statuses:
                logger.info(f"DEBUG: Status final detectado no consumer: {solicitation.status}")
                return False  # Bloqueia acesso ao chat para status finais

            # Verifica se o status permite chat (apenas status ativos permitem chat)
            active_statuses = ['open', 'in_progress', 'waiting_user', 'waiting_third_party']
            if solicitation.status not in active_statuses:
                logger.info(f"DEBUG: Status não ativo detectado no consumer: {solicitation.status}")
                return False  # Bloqueia acesso ao chat para status não ativos

            # Se o usuário for admin, automaticamente adiciona como participante
            if user.is_staff:  # Verifica se é admin
                solicitation.add_participant(user)
                return True
            
            # Verifica se o usuário é participante da solicitação
            return solicitation.is_participant(user)
            
        except Solicitation.DoesNotExist:
            pass

        return False
