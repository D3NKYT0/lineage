from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from core.admin import BaseModelAdmin
from .models import Event


@admin.register(Event)
class EventAdmin(BaseModelAdmin):
    list_display = ('title', 'user', 'start_date', 'end_date', 'get_duration', 'get_status', 'className', 'created_at')
    list_filter = ('user', 'start_date', 'end_date', 'className', 'created_at')
    search_fields = ('title', 'user__username', 'user__email')
    ordering = ('-created_at',)
    list_editable = ('start_date', 'end_date', 'className')
    autocomplete_fields = ['user']
    
    fieldsets = (
        (_('Informações do Evento'), {
            'fields': ('title', 'user')
        }),
        (_('Datas e Horários'), {
            'fields': ('start_date', 'end_date'),
            'description': _('Configure quando o evento acontecerá')
        }),
        (_('Aparência'), {
            'fields': ('className',),
            'description': _('Escolha a cor do evento')
        }),
    )
    
    actions = ['duplicate_events', 'export_events', 'mark_as_completed', 'extend_duration']
    
    def get_duration(self, obj):
        """Calcula e exibe a duração do evento"""
        if obj.start_date and obj.end_date:
            duration = obj.end_date - obj.start_date
            if duration.days > 0:
                if duration.days == 1:
                    return _('1 dia')
                return _('{} dias').format(duration.days)
            else:
                hours = duration.seconds // 3600
                if hours > 0:
                    return _('{} horas').format(hours)
                minutes = (duration.seconds % 3600) // 60
                return _('{} minutos').format(minutes)
        return _('N/A')
    get_duration.short_description = _('Duração')

    def get_status(self, obj):
        """Mostra o status do evento baseado na data"""
        from django.utils import timezone
        now = timezone.now()
        
        if obj.start_date and obj.end_date:
            if now < obj.start_date:
                return format_html(
                    '<span style="background: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
                    _('Agendado')
                )
            elif obj.start_date <= now <= obj.end_date:
                return format_html(
                    '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
                    _('Em Andamento')
                )
            else:
                return format_html(
                    '<span style="background: #6c757d; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
                    _('Concluído')
                )
        return format_html(
            '<span style="background: #ffc107; color: black; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            _('Sem Data')
        )
    get_status.short_description = _('Status')

    def duplicate_events(self, request, queryset):
        """Duplica eventos selecionados"""
        from datetime import timedelta
        
        duplicated_count = 0
        for event in queryset:
            # Criar uma cópia do evento para a próxima semana
            new_event = Event.objects.create(
                title=f"{event.title} (Cópia)",
                user=event.user,
                start_date=event.start_date + timedelta(days=7),
                end_date=event.end_date + timedelta(days=7),
                className=event.className
            )
            duplicated_count += 1
        
        self.message_user(request, _('{} eventos foram duplicados.').format(duplicated_count))
    duplicate_events.short_description = _('Duplicar eventos (próxima semana)')

    def export_events(self, request, queryset):
        """Exporta eventos selecionados"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="eventos_exportados.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            _('Título'), _('Usuário'), _('Data Início'), _('Data Fim'), 
            _('Duração'), _('Cor'), _('Status')
        ])
        
        for event in queryset:
            writer.writerow([
                event.title,
                event.user.username if event.user else '',
                event.start_date.strftime('%d/%m/%Y %H:%M') if event.start_date else '',
                event.end_date.strftime('%d/%m/%Y %H:%M') if event.end_date else '',
                self.get_duration(event),
                event.get_className_display() if event.className else '',
                self.get_status(event).replace('<span style="background: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">', '').replace('</span>', '')
            ])
        
        return response
    export_events.short_description = _('Exportar eventos CSV')

    def mark_as_completed(self, request, queryset):
        """Marca eventos como concluídos (move para o passado)"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        updated_count = 0
        
        for event in queryset:
            if event.start_date and event.start_date > now:
                # Move o evento para o passado
                days_to_subtract = (event.start_date - now).days + 1
                event.start_date = event.start_date - timedelta(days=days_to_subtract)
                event.end_date = event.end_date - timedelta(days=days_to_subtract)
                event.save()
                updated_count += 1
        
        self.message_user(request, _('{} eventos foram marcados como concluídos.').format(updated_count))
    mark_as_completed.short_description = _('Marcar como concluídos')

    def extend_duration(self, request, queryset):
        """Estende a duração dos eventos em 1 hora"""
        from datetime import timedelta
        
        updated_count = 0
        for event in queryset:
            if event.end_date:
                event.end_date = event.end_date + timedelta(hours=1)
                event.save()
                updated_count += 1
        
        self.message_user(request, _('Duração de {} eventos foi estendida em 1 hora.').format(updated_count))
    extend_duration.short_description = _('Estender duração (+1h)')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    class Media:
        css = {
            'all': ('admin/css/event_admin.css',)
        }
        js = ('admin/js/event_admin.js',)
