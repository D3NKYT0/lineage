from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from apps.main.social.models import Post, Comment, ContentFilter, Report, ModerationLog
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Aplica filtros de moderação a todo o conteúdo existente (posts e comentários retroativos)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem aplicar mudanças (apenas simulação)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Número de itens processados por lote (padrão: 100)',
        )
        parser.add_argument(
            '--filter-id',
            type=int,
            help='ID específico do filtro para aplicar (opcional)',
        )
        parser.add_argument(
            '--content-type',
            choices=['posts', 'comments', 'all'],
            default='all',
            help='Tipo de conteúdo para processar (padrão: all)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        filter_id = options.get('filter_id')
        content_type = options['content_type']

        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 MODO SIMULAÇÃO - Nenhuma mudança será aplicada')
            )

        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando aplicação retroativa de filtros de moderação...')
        )

        # Obter filtros ativos
        if filter_id:
            filters = ContentFilter.objects.filter(id=filter_id, is_active=True)
            if not filters.exists():
                self.stdout.write(
                    self.style.ERROR(f'❌ Filtro com ID {filter_id} não encontrado ou inativo')
                )
                return
        else:
            filters = ContentFilter.objects.filter(is_active=True)

        if not filters.exists():
            self.stdout.write(
                self.style.ERROR('❌ Nenhum filtro ativo encontrado. Execute: python manage.py setup_moderation')
            )
            return

        self.stdout.write(f'📊 Filtros ativos encontrados: {filters.count()}')
        
        # Mostrar filtros que serão aplicados
        for f in filters:
            action_emoji = {
                'flag': '🏴',
                'auto_hide': '👁️',
                'auto_delete': '🗑️',
                'notify_moderator': '📧'
            }.get(f.action, '⚠️')
            self.stdout.write(f'   {action_emoji} {f.name} ({f.get_action_display()})')

        # Processar posts
        if content_type in ['posts', 'all']:
            self._process_posts(filters, batch_size, dry_run)

        # Processar comentários
        if content_type in ['comments', 'all']:
            self._process_comments(filters, batch_size, dry_run)

        self.stdout.write(
            self.style.SUCCESS('✅ Aplicação retroativa de filtros concluída!')
        )

    def _process_posts(self, filters, batch_size, dry_run):
        """Processa todos os posts existentes"""
        self.stdout.write('\n📝 Processando Posts...')
        
        # Obter filtros que se aplicam a posts
        post_filters = filters.filter(apply_to_posts=True)
        if not post_filters.exists():
            self.stdout.write('⏭️  Nenhum filtro se aplica a posts')
            return

        total_posts = Post.objects.count()
        processed = 0
        matched_posts = 0
        actions_taken = 0

        self.stdout.write(f'📊 Total de posts para processar: {total_posts}')

        # Processar em lotes
        posts_queryset = Post.objects.all().iterator(chunk_size=batch_size)
        
        for post in posts_queryset:
            processed += 1
            post_matched = False

            # Verificar contra cada filtro
            for content_filter in post_filters:
                if content_filter.matches_content(post.content):
                    post_matched = True
                    if not dry_run:
                        action_applied = self._apply_filter_to_post(content_filter, post)
                        if action_applied:
                            actions_taken += 1
                    else:
                        self.stdout.write(
                            f'   🎯 POST #{post.id}: Filtro "{content_filter.name}" detectou violação'
                        )
                        actions_taken += 1

            if post_matched:
                matched_posts += 1

            # Mostrar progresso a cada lote
            if processed % batch_size == 0:
                self.stdout.write(
                    f'   📈 Progresso: {processed}/{total_posts} posts processados'
                )

        self.stdout.write(f'✅ Posts processados: {processed}')
        self.stdout.write(f'🎯 Posts com violações: {matched_posts}')
        self.stdout.write(f'⚡ Ações aplicadas: {actions_taken}')

    def _process_comments(self, filters, batch_size, dry_run):
        """Processa todos os comentários existentes"""
        self.stdout.write('\n💬 Processando Comentários...')
        
        # Obter filtros que se aplicam a comentários
        comment_filters = filters.filter(apply_to_comments=True)
        if not comment_filters.exists():
            self.stdout.write('⏭️  Nenhum filtro se aplica a comentários')
            return

        total_comments = Comment.objects.count()
        processed = 0
        matched_comments = 0
        actions_taken = 0

        self.stdout.write(f'📊 Total de comentários para processar: {total_comments}')

        # Processar em lotes
        comments_queryset = Comment.objects.all().iterator(chunk_size=batch_size)
        
        for comment in comments_queryset:
            processed += 1
            comment_matched = False

            # Verificar contra cada filtro
            for content_filter in comment_filters:
                if content_filter.matches_content(comment.content):
                    comment_matched = True
                    if not dry_run:
                        action_applied = self._apply_filter_to_comment(content_filter, comment)
                        if action_applied:
                            actions_taken += 1
                    else:
                        self.stdout.write(
                            f'   🎯 COMMENT #{comment.id}: Filtro "{content_filter.name}" detectou violação'
                        )
                        actions_taken += 1

            if comment_matched:
                matched_comments += 1

            # Mostrar progresso a cada lote
            if processed % batch_size == 0:
                self.stdout.write(
                    f'   📈 Progresso: {processed}/{total_comments} comentários processados'
                )

        self.stdout.write(f'✅ Comentários processados: {processed}')
        self.stdout.write(f'🎯 Comentários com violações: {matched_comments}')
        self.stdout.write(f'⚡ Ações aplicadas: {actions_taken}')

    def _apply_filter_to_post(self, content_filter, post):
        """Aplica ação do filtro a um post específico"""
        try:
            with transaction.atomic():
                if content_filter.action == 'flag':
                    # Verificar se já existe denúncia para este post
                    existing_report = Report.objects.filter(
                        reported_post=post,
                        description__contains=content_filter.name
                    ).first()
                    
                    if not existing_report:
                        Report.objects.create(
                            reporter=None,  # Sistema
                            reported_post=post,
                            report_type='spam' if 'spam' in content_filter.name.lower() else 'inappropriate',
                            description=f"Conteúdo filtrado retroativamente: {content_filter.name}",
                            status='pending',
                            priority='medium'
                        )

                elif content_filter.action == 'auto_hide':
                    if post.is_public:  # Só ocultar se ainda estiver público
                        post.is_public = False
                        post.save(update_fields=['is_public'])

                elif content_filter.action == 'auto_delete':
                    post.delete()
                    return True  # Post deletado

                elif content_filter.action == 'notify_moderator':
                    # Criar denúncia de alta prioridade
                    existing_report = Report.objects.filter(
                        reported_post=post,
                        description__contains=content_filter.name
                    ).first()
                    
                    if not existing_report:
                        Report.objects.create(
                            reporter=None,
                            reported_post=post,
                            report_type='inappropriate',
                            description=f"Revisão manual necessária (retroativo): {content_filter.name}",
                            status='pending',
                            priority='high'
                        )

                # Log da ação
                ModerationLog.log_action(
                    moderator=None,
                    action_type='filter_triggered',
                    target_type='post',
                    target_id=post.id if post.pk else 0,
                    description=f"Filtro retroativo aplicado: {content_filter.name}",
                    details=f"Conteúdo: {post.content[:200]}..."
                )

                # Atualizar estatísticas do filtro
                content_filter.matches_count += 1
                content_filter.last_matched = timezone.now()
                content_filter.save(update_fields=['matches_count', 'last_matched'])

                return True

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao aplicar filtro ao post {post.id}: {e}')
            )
            return False

    def _apply_filter_to_comment(self, content_filter, comment):
        """Aplica ação do filtro a um comentário específico"""
        try:
            with transaction.atomic():
                if content_filter.action == 'flag':
                    # Verificar se já existe denúncia para este comentário
                    existing_report = Report.objects.filter(
                        reported_comment=comment,
                        description__contains=content_filter.name
                    ).first()
                    
                    if not existing_report:
                        Report.objects.create(
                            reporter=None,
                            reported_comment=comment,
                            report_type='spam' if 'spam' in content_filter.name.lower() else 'inappropriate',
                            description=f"Comentário filtrado retroativamente: {content_filter.name}",
                            status='pending',
                            priority='medium'
                        )

                elif content_filter.action == 'auto_hide':
                    # Para comentários, podemos implementar um campo is_visible
                    # Por enquanto, vamos apenas logar
                    pass

                elif content_filter.action == 'auto_delete':
                    comment.delete()
                    return True  # Comentário deletado

                elif content_filter.action == 'notify_moderator':
                    existing_report = Report.objects.filter(
                        reported_comment=comment,
                        description__contains=content_filter.name
                    ).first()
                    
                    if not existing_report:
                        Report.objects.create(
                            reporter=None,
                            reported_comment=comment,
                            report_type='inappropriate',
                            description=f"Comentário requer revisão (retroativo): {content_filter.name}",
                            status='pending',
                            priority='high'
                        )

                # Log da ação
                ModerationLog.log_action(
                    moderator=None,
                    action_type='filter_triggered',
                    target_type='comment',
                    target_id=comment.id if comment.pk else 0,
                    description=f"Filtro retroativo aplicado: {content_filter.name}",
                    details=f"Conteúdo: {comment.content[:200]}..."
                )

                # Atualizar estatísticas do filtro
                content_filter.matches_count += 1
                content_filter.last_matched = timezone.now()
                content_filter.save(update_fields=['matches_count', 'last_matched'])

                return True

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao aplicar filtro ao comentário {comment.id}: {e}')
            )
            return False
