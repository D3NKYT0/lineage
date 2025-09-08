from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.main.social.models import ModerationAction

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa o sistema de login com usuários suspensos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nome do usuário para testar',
        )
        parser.add_argument(
            '--action',
            type=str,
            choices=['suspend', 'ban', 'reactivate'],
            help='Ação a ser executada',
        )
        parser.add_argument(
            '--duration',
            type=int,
            default=7,
            help='Duração da suspensão em dias (padrão: 7)',
        )
        parser.add_argument(
            '--reason',
            type=str,
            default='Teste de suspensão',
            help='Motivo da suspensão',
        )

    def handle(self, *args, **options):
        username = options['username']
        action = options['action']
        duration = options['duration']
        reason = options['reason']

        if not username:
            self.stdout.write(self.style.ERROR('❌ Username é obrigatório'))
            return

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Usuário "{username}" não encontrado'))
            return

        if action == 'suspend':
            self.suspend_user(user, duration, reason)
        elif action == 'ban':
            self.ban_user(user, reason)
        elif action == 'reactivate':
            self.reactivate_user(user)
        else:
            self.show_user_status(user)

    def suspend_user(self, user, duration, reason):
        """Suspende um usuário temporariamente"""
        if not user.is_active:
            self.stdout.write(self.style.WARNING(f'⚠️ Usuário "{user.username}" já está inativo'))
            return

        # Desativa o usuário
        user.is_active = False
        user.save()

        # Cria a ação de moderação
        suspension_action = ModerationAction.objects.create(
            moderator=User.objects.filter(is_superuser=True).first(),
            action_type='suspend_user',
            reason=reason,
            target_user=user,
            suspension_duration=timedelta(days=duration),
            suspension_type='temporary',
            notify_user=True,
            notification_message=f'Você foi suspenso por {duration} dias. Motivo: {reason}'
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Usuário "{user.username}" suspenso por {duration} dias\n'
                f'📅 Suspenso até: {suspension_action.suspension_end_date}\n'
                f'📋 Motivo: {reason}'
            )
        )

    def ban_user(self, user, reason):
        """Bane um usuário permanentemente"""
        if not user.is_active:
            self.stdout.write(self.style.WARNING(f'⚠️ Usuário "{user.username}" já está inativo'))
            return

        # Desativa o usuário
        user.is_active = False
        user.save()

        # Cria a ação de moderação
        ban_action = ModerationAction.objects.create(
            moderator=User.objects.filter(is_superuser=True).first(),
            action_type='ban_user',
            reason=reason,
            target_user=user,
            suspension_type='permanent',
            notify_user=True,
            notification_message=f'Você foi banido permanentemente. Motivo: {reason}'
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'🔴 Usuário "{user.username}" banido permanentemente\n'
                f'📋 Motivo: {reason}'
            )
        )

    def reactivate_user(self, user):
        """Reativa um usuário"""
        if user.is_active:
            self.stdout.write(self.style.WARNING(f'⚠️ Usuário "{user.username}" já está ativo'))
            return

        # Reativa o usuário
        user.is_active = True
        user.save()

        # Desativa as ações de moderação ativas
        ModerationAction.objects.filter(
            target_user=user,
            action_type__in=['suspend_user', 'ban_user'],
            is_active=True
        ).update(is_active=False)

        self.stdout.write(
            self.style.SUCCESS(f'✅ Usuário "{user.username}" reativado com sucesso')
        )

    def show_user_status(self, user):
        """Mostra o status atual do usuário"""
        self.stdout.write(f'\n📊 Status do usuário "{user.username}":')
        self.stdout.write(f'   🔓 Ativo: {"✅ Sim" if user.is_active else "❌ Não"}')
        self.stdout.write(f'   👤 Nome: {user.get_full_name() or "Não informado"}')
        self.stdout.write(f'   📧 Email: {user.email}')
        self.stdout.write(f'   📅 Criado em: {user.date_joined.strftime("%d/%m/%Y às %H:%M")}')

        if not user.is_active:
            # Busca ações de moderação ativas
            active_actions = ModerationAction.objects.filter(
                target_user=user,
                action_type__in=['suspend_user', 'ban_user'],
                is_active=True
            ).order_by('-created_at')

            if active_actions:
                self.stdout.write(f'\n🚫 Ações de moderação ativas:')
                for action in active_actions:
                    self.stdout.write(f'   🔴 {action.get_action_type_display()}')
                    self.stdout.write(f'   📋 Motivo: {action.reason}')
                    self.stdout.write(f'   👤 Moderador: {action.moderator.username}')
                    self.stdout.write(f'   📅 Data: {action.created_at.strftime("%d/%m/%Y às %H:%M")}')
                    
                    if action.suspension_end_date:
                        if action.suspension_end_date < timezone.now():
                            self.stdout.write(f'   ⏰ Status: EXPIRADA (era até {action.suspension_end_date.strftime("%d/%m/%Y às %H:%M")})')
                        else:
                            self.stdout.write(f'   ⏰ Válida até: {action.suspension_end_date.strftime("%d/%m/%Y às %H:%M")}')
                    
                    self.stdout.write('')
            else:
                self.stdout.write(f'\n⚠️ Usuário inativo sem registro de suspensão/banimento')
