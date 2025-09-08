import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from django.utils import timezone

logger = logging.getLogger(__name__)


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            raise DenyConnection("User not authenticated")

        self.user = self.scope["user"]
        self.user_group_name = f"user_{self.user.id}"
        
        # Adicionar ao grupo do usuário
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Marcar usuário como ativo
        await self.set_user_active()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'send_message':
                await self.handle_send_message(data)
            elif message_type == 'load_messages':
                await self.handle_load_messages(data)
            elif message_type == 'mark_as_read':
                await self.handle_mark_as_read(data)
            elif message_type == 'user_activity':
                await self.set_user_active()
            elif message_type == 'get_unread_count':
                await self.handle_get_unread_count()
            elif message_type == 'get_friends_stats':
                await self.handle_get_friends_stats()
            elif message_type == 'get_friends_status':
                await self.handle_get_friends_status()
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Internal server error'
            }))

    async def handle_send_message(self, data):
        message_text = data.get('message', '').strip()
        friend_id = data.get('friend_id')
        
        if not message_text or len(message_text) > 500:
            await self.send(text_data=json.dumps({
                'error': 'Invalid message'
            }))
            return
            
        if not friend_id:
            await self.send(text_data=json.dumps({
                'error': 'Friend ID required'
            }))
            return
            
        # Verificar se são amigos
        are_friends = await self.check_friendship(friend_id)
        if not are_friends:
            await self.send(text_data=json.dumps({
                'error': 'You can only send messages to friends'
            }))
            return
            
        # Salvar mensagem
        message = await self.save_message(friend_id, message_text)
        if not message:
            await self.send(text_data=json.dumps({
                'error': 'Failed to save message'
            }))
            return
            
        # Enviar para o destinatário
        friend_group_name = f"user_{friend_id}"
        await self.channel_layer.group_send(
            friend_group_name,
            {
                'type': 'new_message',
                'message': message_text,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'sender_avatar_url': await self.get_avatar_url(self.user),
                'timestamp': message.timestamp.isoformat(),
                'chat_id': message.chat.id
            }
        )
        
        # Confirmar envio para o remetente
        await self.send(text_data=json.dumps({
            'type': 'message_sent',
            'message': message_text,
            'timestamp': message.timestamp.isoformat(),
            'chat_id': message.chat.id
        }))

    async def handle_load_messages(self, data):
        friend_id = data.get('friend_id')
        
        if not friend_id:
            await self.send(text_data=json.dumps({
                'error': 'Friend ID required'
            }))
            return
            
        # Verificar se são amigos
        are_friends = await self.check_friendship(friend_id)
        if not are_friends:
            await self.send(text_data=json.dumps({
                'error': 'You can only load messages from friends'
            }))
            return
            
        # Carregar mensagens
        messages = await self.load_messages(friend_id)
        
        # Marcar como lidas
        await self.mark_messages_as_read(friend_id)
        
        await self.send(text_data=json.dumps({
            'type': 'messages_loaded',
            'messages': messages
        }))

    async def handle_mark_as_read(self, data):
        friend_id = data.get('friend_id')
        
        if friend_id:
            await self.mark_messages_as_read(friend_id)
            await self.send(text_data=json.dumps({
                'type': 'messages_marked_read',
                'friend_id': friend_id
            }))

    async def handle_get_unread_count(self):
        unread_counts = await self.get_unread_counts()
        await self.send(text_data=json.dumps({
            'type': 'unread_counts',
            'unread_counts': unread_counts
        }))

    async def handle_get_friends_stats(self):
        """Obter estatísticas de amigos via WebSocket"""
        stats = await self.get_friends_stats()
        await self.send(text_data=json.dumps({
            'type': 'friends_stats',
            'stats': stats
        }))

    async def handle_get_friends_status(self):
        """Obter status online/offline dos amigos via WebSocket"""
        friends_status = await self.get_friends_status()
        await self.send(text_data=json.dumps({
            'type': 'friends_status',
            'friends_status': friends_status
        }))

    async def new_message(self, event):
        """Enviar nova mensagem para o usuário"""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'sender_avatar_url': event['sender_avatar_url'],
            'timestamp': event['timestamp'],
            'chat_id': event['chat_id']
        }))

    @database_sync_to_async
    def check_friendship(self, friend_id):
        """Verificar se dois usuários são amigos"""
        try:
            from .models import Friendship
            return Friendship.objects.filter(
                user=self.user,
                friend_id=friend_id,
                accepted=True
            ).exists()
        except Exception as e:
            logger.error(f"Error checking friendship: {str(e)}")
            return False

    @database_sync_to_async
    def save_message(self, friend_id, message_text):
        """Salvar mensagem no banco de dados"""
        try:
            from apps.main.home.models import User
            from .models import Message
            
            friend = User.objects.get(id=friend_id)
            chat = self.create_or_get_chat_sync(friend)
            
            message = Message.objects.create(
                chat=chat,
                text=message_text,
                sender=self.user
            )
            
            # Atualizar última mensagem do chat
            chat.last_message = message_text
            chat.last_updated = timezone.now()
            chat.save()
            
            return message
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            return None

    def create_or_get_chat_sync(self, friend):
        """Criar ou obter chat entre dois usuários (versão síncrona)"""
        from .models import Chat
        user1, user2 = sorted([self.user, friend], key=lambda u: u.id)
        chat, created = Chat.objects.get_or_create(user1=user1, user2=user2)
        return chat

    @database_sync_to_async
    def load_messages(self, friend_id):
        """Carregar mensagens de um chat"""
        try:
            from apps.main.home.models import User
            
            friend = User.objects.get(id=friend_id)
            chat = self.create_or_get_chat_sync(friend)
            
            messages = chat.messages.all().select_related('sender').order_by('timestamp')[:500]
            
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    'text': msg.text,
                    'sender': {
                        'username': msg.sender.username,
                        'avatar_url': self.get_avatar_url_sync(msg.sender)
                    },
                    'timestamp': msg.timestamp.isoformat(),
                    'is_read': msg.is_read,
                    'is_own': msg.sender == self.user
                })
            
            return formatted_messages
        except Exception as e:
            logger.error(f"Error loading messages: {str(e)}")
            return []

    @database_sync_to_async
    def mark_messages_as_read(self, friend_id):
        """Marcar mensagens como lidas"""
        try:
            from apps.main.home.models import User
            
            friend = User.objects.get(id=friend_id)
            chat = self.create_or_get_chat_sync(friend)
            
            # Marcar mensagens do amigo como lidas
            chat.messages.filter(
                sender=friend,
                is_read=False
            ).update(is_read=True)
            
        except Exception as e:
            logger.error(f"Error marking messages as read: {str(e)}")

    @database_sync_to_async
    def get_unread_counts(self):
        """Obter contagem de mensagens não lidas por amigo"""
        try:
            from .models import Friendship
            from apps.main.home.models import User
            
            friendships = Friendship.objects.filter(
                user=self.user,
                accepted=True
            ).values('friend_id')
            
            unread_counts = {}
            for friendship in friendships:
                friend_id = friendship['friend_id']
                friend = User.objects.get(id=friend_id)
                chat = self.create_or_get_chat_sync(friend)
                
                unread_count = chat.messages.filter(
                    sender=friend,
                    is_read=False
                ).count()
                
                unread_counts[friend_id] = unread_count
            
            return unread_counts
        except Exception as e:
            logger.error(f"Error getting unread counts: {str(e)}")
            return {}

    @database_sync_to_async
    def set_user_active(self):
        """Marcar usuário como ativo"""
        try:
            from django.core.cache import cache
            cache.set(f"user_activity_{self.user.id}", timezone.now(), timeout=300)
        except Exception as e:
            logger.error(f"Error setting user active: {str(e)}")

    @database_sync_to_async
    def get_avatar_url(self, user):
        """Obter URL do avatar do usuário"""
        return self.get_avatar_url_sync(user)

    def get_avatar_url_sync(self, user):
        """Obter URL do avatar do usuário (versão síncrona)"""
        if user.avatar:
            from django.urls import reverse
            from django.utils import timezone
            timestamp = int(timezone.now().timestamp())
            return reverse('serve_files:serve_decrypted_file_with_timestamp', 
                         kwargs={'app_name': 'home', 'model_name': 'user', 'field_name': 'avatar', 
                                'uuid': user.uuid, 'timestamp': timestamp})
        else:
            return '/static/assets/img/team/generic_user.png'

    @database_sync_to_async
    def get_friends_stats(self):
        """Obter estatísticas de amigos"""
        try:
            from .models import Friendship
            
            # Contar amigos aceitos
            total_friends = Friendship.objects.filter(
                user=self.user, 
                accepted=True
            ).count()
            
            # Contar solicitações pendentes recebidas
            total_pending_requests = Friendship.objects.filter(
                friend=self.user, 
                accepted=False
            ).count()
            
            # Contar solicitações enviadas
            total_sent_requests = Friendship.objects.filter(
                user=self.user, 
                accepted=False
            ).count()
            
            return {
                'total_friends': total_friends,
                'total_pending_requests': total_pending_requests,
                'total_sent_requests': total_sent_requests,
            }
        except Exception as e:
            logger.error(f"Error getting friends stats: {str(e)}")
            return {
                'total_friends': 0,
                'total_pending_requests': 0,
                'total_sent_requests': 0,
            }

    @database_sync_to_async
    def get_friends_status(self):
        """Obter status online/offline dos amigos"""
        try:
            from .models import Friendship
            from django.core.cache import cache
            
            # Obter todos os amigos aceitos
            friendships = Friendship.objects.filter(
                user=self.user, 
                accepted=True
            ).select_related('friend')
            
            friends_status = {}
            for friendship in friendships:
                friend = friendship.friend
                # Verificar se o usuário está ativo (última atividade nos últimos 5 minutos)
                last_activity = cache.get(f"user_activity_{friend.id}")
                is_online = False
                
                if last_activity:
                    from datetime import timedelta
                    if timezone.now() - last_activity < timedelta(minutes=5):
                        is_online = True
                
                friends_status[friend.id] = {
                    'is_online': is_online,
                    'username': friend.username
                }
            
            return friends_status
        except Exception as e:
            logger.error(f"Error getting friends status: {str(e)}")
            return {} 