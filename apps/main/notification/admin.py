# admin.py

from django.contrib import admin
from .models import Notification, PublicNotificationView, PushSubscription, PushNotificationLog
from core.admin import BaseModelAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


@admin.register(Notification)
class NotificationAdmin(BaseModelAdmin):
    list_display = ('user', 'notification_type', 'message', 'viewed', 'created_at', 'notification_link')
    list_filter = ('notification_type', 'viewed', 'created_at')
    search_fields = ('user__username', 'message', 'link')
    readonly_fields = ('created_at', 'updated_at', 'notification_link')
    fields = ('user', 'notification_type', 'message', 'link', 'viewed', 'notification_link', 'created_at', 'updated_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')

    def notification_link(self, obj):
        if obj.link:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.link, _("Abrir link"))
        return "-"
    notification_link.short_description = _("Link de Redirecionamento")


@admin.register(PublicNotificationView)
class PublicNotificationViewAdmin(BaseModelAdmin):
    list_display = ('user', 'notification', 'viewed')
    list_filter = ('viewed',)
    search_fields = ('user__username', 'notification__message')


@admin.register(PushSubscription)
class PushSubscriptionAdmin(BaseModelAdmin):
    list_display = ("user", "endpoint", "created_at")
    search_fields = ("user__username", "endpoint")


@admin.register(PushNotificationLog)
class PushNotificationLogAdmin(BaseModelAdmin):
    list_display = ("sent_by", "message", "total_subscribers", "successful_sends", "failed_sends", "created_at")
    list_filter = ("created_at", "sent_by")
    search_fields = ("sent_by__username", "message")
    readonly_fields = ("created_at", "updated_at")
    fields = ("sent_by", "message", "total_subscribers", "successful_sends", "failed_sends", "created_at", "updated_at")
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('sent_by')
