from django.contrib import admin
from .models import Friendship, Chat, Message
from core.admin import BaseModelAdmin


@admin.register(Friendship)
class FriendshipAdmin(BaseModelAdmin):
    list_display = ('user', 'friend', 'created_at', 'accepted')
    list_filter = ('accepted', 'created_at')
    search_fields = ('user__username', 'friend__username')
    ordering = ('-created_at',)


@admin.register(Chat)
class ChatAdmin(BaseModelAdmin):
    list_display = ('user1', 'user2', 'last_message', 'last_updated')  # Atualize aqui
    list_filter = ('last_updated',)
    search_fields = ('user1__username', 'user2__username')  # Atualize aqui
    ordering = ('-last_updated',)


@admin.register(Message)
class MessageAdmin(BaseModelAdmin):
    list_display = ('chat', 'sender', 'text', 'timestamp')
    list_filter = ('sender', 'timestamp')
    search_fields = ('text', 'sender__username')
    ordering = ('-timestamp',)
