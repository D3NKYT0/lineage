from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from apps.main.social.models import ContentFilter


class Command(BaseCommand):
    help = 'Remove todos os filtros de moderação do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a remoção sem confirmação',
        )
        parser.add_argument(
            '--keep-defaults',
            action='store_true',
            help='Mantém apenas os filtros padrão do sistema',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra quais filtros seriam removidos sem executar',
        )

    def handle(self, *args, **options):
        force = options['force']
        keep_defaults = options['keep_defaults']
        dry_run = options['dry_run']

        # Obter todos os filtros
        if keep_defaults:
            # Manter apenas filtros padrão do sistema
            filters_to_remove = ContentFilter.objects.exclude(
                name__in=[
                    'Padrão de Spam Automático',
                    'Spam - Ofertas Comerciais Agressivas',
                    'Spam - Medicamentos e Suplementos',
                    'Spam - Esquemas Financeiros Suspeitos',
                    'Palavrões - Português (Leve)',
                    'Palavrões - Português (Severo)',
                    'Palavrões com Símbolos',
                    'Conteúdo Pornográfico Explícito',
                    'Sites Pornográficos',
                    'Encurtadores de URL Suspeitos',
                    'Domínios Suspeitos de Phishing',
                    'Múltiplas URLs (Spam)',
                    'Discurso de Ódio Racial',
                    'Discurso de Ódio Homofóbico',
                    'Fake News Médicas',
                    'Conteúdo Repetitivo (Spam)',
                    'CAPS Excessivo',
                    'Informações Pessoais',
                    'Golpes Brasileiros - PIX',
                    'Sites de Apostas Brasileiros'
                ]
            )
            action_description = "removendo filtros personalizados (mantendo padrões)"
        else:
            # Remover todos os filtros
            filters_to_remove = ContentFilter.objects.all()
            action_description = "removendo TODOS os filtros"

        total_filters = filters_to_remove.count()

        if total_filters == 0:
            self.stdout.write(
                self.style.WARNING('Nenhum filtro encontrado para remoção.')
            )
            return

        # Mostrar filtros que serão removidos
        self.stdout.write(
            self.style.WARNING(f'\n{"="*60}')
        )
        self.stdout.write(
            self.style.WARNING(f'🗑️  LIMPEZA DE FILTROS DE MODERAÇÃO')
        )
        self.stdout.write(
            self.style.WARNING(f'{"="*60}')
        )
        
        self.stdout.write(f'\n📋 Ação: {action_description}')
        self.stdout.write(f'📊 Total de filtros: {total_filters}')
        
        if dry_run:
            self.stdout.write(f'🔍 Modo: SIMULAÇÃO (dry-run)')
        else:
            self.stdout.write(f'🔍 Modo: EXECUÇÃO REAL')

        # Listar filtros que serão removidos
        self.stdout.write(f'\n📝 Filtros que serão removidos:')
        self.stdout.write(f'{"-"*50}')
        
        for i, filter_obj in enumerate(filters_to_remove, 1):
            status_icon = "🟢" if filter_obj.is_active else "🔴"
            self.stdout.write(
                f'{i:2d}. {status_icon} {filter_obj.name} ({filter_obj.get_filter_type_display()})'
            )

        # Confirmação (se não for force e não for dry-run)
        if not force and not dry_run:
            self.stdout.write(f'\n{"-"*60}')
            self.stdout.write(
                self.style.ERROR('⚠️  ATENÇÃO: Esta ação é irreversível!')
            )
            self.stdout.write(
                self.style.ERROR('Todos os filtros listados acima serão PERMANENTEMENTE removidos.')
            )
            
            confirm = input('\n❓ Confirma a remoção? (digite "SIM" para confirmar): ')
            
            if confirm.upper() != 'SIM':
                self.stdout.write(
                    self.style.WARNING('❌ Operação cancelada pelo usuário.')
                )
                return

        # Executar remoção
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ SIMULAÇÃO: {total_filters} filtros seriam removidos')
            )
            self.stdout.write(
                self.style.SUCCESS('Para executar realmente, remova a opção --dry-run')
            )
        else:
            # Fazer backup dos filtros antes de remover
            backup_data = []
            for filter_obj in filters_to_remove:
                backup_data.append({
                    'name': filter_obj.name,
                    'filter_type': filter_obj.filter_type,
                    'pattern': filter_obj.pattern,
                    'action': filter_obj.action,
                    'description': filter_obj.description,
                    'case_sensitive': filter_obj.case_sensitive,
                    'apply_to_posts': filter_obj.apply_to_posts,
                    'apply_to_comments': filter_obj.apply_to_comments,
                    'apply_to_usernames': filter_obj.apply_to_usernames,
                    'is_active': filter_obj.is_active,
                    'matches_count': filter_obj.matches_count,
                    'last_matched': filter_obj.last_matched,
                })

            # Remover filtros
            deleted_count = filters_to_remove.delete()[0]

            # Mostrar resultado
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ SUCESSO: {deleted_count} filtros removidos!')
            )

            # Salvar backup em arquivo (opcional)
            if backup_data:
                import json
                from datetime import datetime
                
                backup_filename = f'filters_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                
                try:
                    with open(backup_filename, 'w', encoding='utf-8') as f:
                        json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'💾 Backup salvo em: {backup_filename}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Erro ao salvar backup: {e}')
                    )

        # Estatísticas finais
        remaining_filters = ContentFilter.objects.count()
        active_filters = ContentFilter.objects.filter(is_active=True).count()
        
        self.stdout.write(f'\n📊 Estatísticas finais:')
        self.stdout.write(f'   • Filtros restantes: {remaining_filters}')
        self.stdout.write(f'   • Filtros ativos: {active_filters}')
        
        if remaining_filters == 0:
            self.stdout.write(
                self.style.WARNING('⚠️  Nenhum filtro restante no sistema!')
            )
            self.stdout.write(
                self.style.WARNING('Execute "python manage.py setup_moderation" para recriar os filtros padrão.')
            )
        
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(
            self.style.SUCCESS('🎉 Limpeza de filtros concluída!')
        )
        self.stdout.write(f'{"="*60}')
