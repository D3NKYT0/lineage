from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import Post, Comment, ContentFilter, Report, ModerationLog, ReportFilterFlag
import re


@receiver(post_save, sender=Post)
def apply_content_filters_to_post(sender, instance, created, **kwargs):
    """Aplica filtros de conteúdo automaticamente quando um post é criado"""
    if not created:
        return
    
    # Obter filtros ativos para posts
    active_filters = ContentFilter.objects.filter(
        is_active=True,
        apply_to_posts=True
    )
    
    if not active_filters.exists():
        return
    
    # Verificar o conteúdo do post
    content_to_check = instance.content
    if not content_to_check:
        return
    
    # Coletar filtros acionados para consolidar mensagens
    triggered_filters = {
        'flag': [],
        'auto_hide': [],
        'auto_delete': [],
        'notify_moderator': []
    }
    
    for content_filter in active_filters:
        if content_filter.matches_content(content_to_check):
            apply_filter_action(content_filter, instance, 'post', triggered_filters)
    
    # Mostrar mensagens consolidadas (se há uma request disponível no contexto)
    try:
        current_request = getattr(instance, '_current_request', None)
        if current_request:
            show_consolidated_messages(current_request, triggered_filters)
    except:
        pass  # Não há request disponível, pular mensagens


@receiver(post_save, sender=Comment)
def apply_content_filters_to_comment(sender, instance, created, **kwargs):
    """Aplica filtros de conteúdo automaticamente quando um comentário é criado"""
    if not created:
        return
    
    # Obter filtros ativos para comentários
    active_filters = ContentFilter.objects.filter(
        is_active=True,
        apply_to_comments=True
    )
    
    if not active_filters.exists():
        return
    
    # Verificar o conteúdo do comentário
    content_to_check = instance.content
    if not content_to_check:
        return
    
    # Coletar filtros acionados para consolidar mensagens
    triggered_filters = {
        'flag': [],
        'auto_hide': [],
        'auto_delete': [],
        'notify_moderator': []
    }
    
    for content_filter in active_filters:
        if content_filter.matches_content(content_to_check):
            apply_filter_action(content_filter, instance, 'comment', triggered_filters)
    
    # Mostrar mensagens consolidadas (se há uma request disponível no contexto)
    try:
        current_request = getattr(instance, '_current_request', None)
        if current_request:
            show_consolidated_messages(current_request, triggered_filters)
    except:
        pass  # Não há request disponível, pular mensagens


def apply_filter_action(content_filter, content_instance, content_type, triggered_filters=None):
    """Aplica a ação do filtro ao conteúdo"""
    try:
        # Determinar campos baseados no tipo de conteúdo
        if content_type == 'post':
            content_id = content_instance.id
            author = content_instance.author
        elif content_type == 'comment':
            content_id = content_instance.id
            author = content_instance.author
        else:
            return
        
        # Aplicar ação baseada no tipo
        if content_filter.action == 'flag':
            # Buscar ou criar report consolidado para este conteúdo
            existing_report = None
            if content_type == 'post':
                existing_report = Report.objects.filter(
                    reported_post=content_instance,
                    reporter__isnull=True,  # Reports do sistema
                    status='pending'
                ).first()
            elif content_type == 'comment':
                existing_report = Report.objects.filter(
                    reported_comment=content_instance,
                    reporter__isnull=True,  # Reports do sistema
                    status='pending'
                ).first()
            
            if existing_report:
                # Adicionar flag ao report existente
                report = existing_report
                # Atualizar descrição para incluir novo filtro
                current_filters = [flag.content_filter.name for flag in report.filter_flags.all()]
                if content_filter.name not in current_filters:
                    report.description = f"Conteúdo filtrado por múltiplos filtros: {', '.join(current_filters + [content_filter.name])}"
                    report.save()
            else:
                # Criar novo report consolidado
                report = Report.objects.create(
                    reporter=None,  # Sistema
                    report_type='spam' if 'spam' in content_filter.name.lower() else 'inappropriate',
                    description=f"Conteúdo filtrado automaticamente pelo filtro: {content_filter.name}",
                    status='pending',
                    priority='medium'
                )
                
                # Associar o conteúdo à denúncia
                if content_type == 'post':
                    report.reported_post = content_instance
                elif content_type == 'comment':
                    report.reported_comment = content_instance
                report.save()
            
            # Adicionar flag do filtro ao report
            matched_pattern = _extract_matched_pattern(content_instance.content, content_filter)
            report.add_filter_flag(
                content_filter=content_filter,
                matched_pattern=matched_pattern,
                confidence=1.0
            )
            
            # Log da ação
            ModerationLog.log_action(
                moderator=None,  # Sistema
                action_type='filter_triggered',
                target_type=content_type,
                target_id=content_id,
                description=f"Filtro '{content_filter.name}' acionado - Conteúdo marcado para revisão",
                details=f"Padrão detectado: {content_filter.pattern[:100]}...\nConteúdo: {content_instance.content[:200]}..."
            )
            
            # Registrar filtro acionado
            if triggered_filters is not None:
                triggered_filters['flag'].append(content_filter.name)
            
        elif content_filter.action == 'auto_hide':
            # Ocultar conteúdo automaticamente
            if content_type == 'post':
                content_instance.is_public = False
                content_instance.save()
            elif content_type == 'comment':
                # Para comentários, podemos implementar um campo is_hidden
                # Por enquanto, deletar o comentário
                # Verificar se o comentário tem ID antes de tentar deletar
                if content_instance.id is None:
                    # Se não tem ID, não pode deletar - apenas logar o erro
                    print(f"Erro: Tentativa de deletar comentário sem ID - Filtro: {content_filter.name}")
                    ModerationLog.log_action(
                        moderator=None,
                        action_type='filter_triggered',
                        target_type='system',
                        target_id=0,
                        description="Erro: Tentativa de deletar comentário sem ID",
                        details=f"Filtro: {content_filter.name}\nConteúdo: {content_instance.content[:200]}..."
                    )
                    return
                
                content_instance.delete()
                return  # Não continuar processamento se deletado
            
            # Log da ação
            ModerationLog.log_action(
                moderator=None,  # Sistema
                action_type='content_hidden',
                target_type=content_type,
                target_id=content_id,
                description=f"Conteúdo ocultado automaticamente pelo filtro: {content_filter.name}",
                details=f"Padrão detectado: {content_filter.pattern[:100]}...\nConteúdo: {content_instance.content[:200]}..."
            )
            
            # Registrar filtro acionado
            if triggered_filters is not None:
                triggered_filters['auto_hide'].append(content_filter.name)
            
        elif content_filter.action == 'auto_delete':
            # Registrar filtro acionado antes de deletar
            if triggered_filters is not None:
                triggered_filters['auto_delete'].append(content_filter.name)
            
            # Verificar se o conteúdo tem ID antes de tentar deletar
            if content_instance.id is None:
                # Se não tem ID, não pode deletar - apenas logar o erro
                print(f"Erro: Tentativa de deletar {content_type} sem ID - Filtro: {content_filter.name}")
                ModerationLog.log_action(
                    moderator=None,
                    action_type='filter_triggered',
                    target_type='system',
                    target_id=0,
                    description=f"Erro: Tentativa de deletar {content_type} sem ID",
                    details=f"Filtro: {content_filter.name}\nConteúdo: {content_instance.content[:200]}..."
                )
                return
            
            # Deletar conteúdo automaticamente
            content_instance.delete()
            
            # Log da ação (com ID que pode não existir mais)
            ModerationLog.log_action(
                moderator=None,  # Sistema
                action_type='content_deleted',
                target_type=content_type,
                target_id=content_id,
                description=f"Conteúdo deletado automaticamente pelo filtro: {content_filter.name}",
                details=f"Padrão detectado: {content_filter.pattern[:100]}...\nConteúdo: {content_instance.content[:200]}..."
            )
            return  # Não continuar processamento se deletado
            
        elif content_filter.action == 'notify_moderator':
            # Notificar moderadores (criar denúncia com prioridade alta)
            report = Report.objects.create(
                reporter=None,  # Sistema
                report_type='inappropriate',
                description=f"Conteúdo requer revisão manual - Filtro: {content_filter.name}",
                status='pending',
                priority='high'
            )
            
            # Associar o conteúdo à denúncia
            if content_type == 'post':
                report.reported_post = content_instance
            elif content_type == 'comment':
                report.reported_comment = content_instance
            report.save()
            
            # Log da ação
            ModerationLog.log_action(
                moderator=None,  # Sistema
                action_type='report_created',
                target_type=content_type,
                target_id=content_id,
                description=f"Moderadores notificados pelo filtro: {content_filter.name}",
                details=f"Padrão detectado: {content_filter.pattern[:100]}...\nConteúdo: {content_instance.content[:200]}..."
            )
            
            # Registrar filtro acionado
            if triggered_filters is not None:
                triggered_filters['notify_moderator'].append(content_filter.name)
        
        # Atualizar estatísticas do filtro
        content_filter.matches_count += 1
        content_filter.last_matched = timezone.now()
        content_filter.save(update_fields=['matches_count', 'last_matched'])
        
    except Exception as e:
        # Log de erro, mas não falhar a criação do conteúdo
        print(f"Erro ao aplicar filtro de conteúdo: {e}")
        ModerationLog.log_action(
            moderator=None,
            action_type='filter_triggered',
            target_type='system',
            target_id=0,
            description="Erro ao aplicar filtro de conteúdo",
            details=f"Erro: {str(e)}\nFiltro: {content_filter.name}"
        )


def check_spam_patterns(content):
    """Verifica padrões comuns de spam"""
    if not content:
        return False
    
    # Padrões de spam em português e inglês
    spam_patterns = [
        # Palavras de ganho fácil
        r'\b(ganhe|ganhar|dinheiro|fácil|rápido|grátis|free|money|earn|easy)\b',
        r'\b(clique|click|here|aqui|agora|now|urgente|urgent)\b',
        
        # Frases comuns de spam
        r'ganhe? dinheiro',
        r'dinheiro fácil',
        r'renda extra',
        r'trabalhe em casa',
        r'oportunidade única',
        r'limited time',
        r'act now',
        r'click here',
        
        # URLs suspeitas
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        
        # Múltiplos sinais de exclamação ou interrogação
        r'[!]{3,}',
        r'[?]{3,}',
        
        # Texto em caixa alta excessivo
        r'\b[A-Z]{10,}\b',
    ]
    
    content_lower = content.lower()
    
    for pattern in spam_patterns:
        if re.search(pattern, content_lower, re.IGNORECASE):
            return True
    
    return False


def show_consolidated_messages(request, triggered_filters):
    """Exibe mensagens consolidadas dos filtros acionados"""
    if not request.user.is_authenticated:
        return
    
    # Consolidar mensagens por tipo de ação
    if triggered_filters['flag']:
        messages.warning(
            request, 
            _('Seu conteúdo foi marcado para revisão por nossos filtros automáticos.')
        )
    
    if triggered_filters['auto_hide']:
        messages.info(
            request, 
            _('Seu conteúdo foi ocultado automaticamente devido aos nossos filtros.')
        )
    
    if triggered_filters['auto_delete']:
        messages.error(
            request, 
            _('Seu conteúdo foi removido por violar nossas diretrizes.')
        )
    
    if triggered_filters['notify_moderator']:
        messages.info(
            request, 
            _('Seu conteúdo será revisado pela equipe de moderação.')
        )


def _extract_matched_pattern(content, content_filter):
    """Extrai o padrão específico que foi detectado no conteúdo"""
    try:
        if content_filter.filter_type == 'keyword':
            # Para palavras-chave, retornar a palavra encontrada
            pattern = content_filter.pattern.lower()
            content_lower = content.lower() if not content_filter.case_sensitive else content
            
            # Verificar se a palavra existe no conteúdo
            if pattern in content_lower:
                # Encontrar a posição e extrair contexto
                start_pos = content_lower.find(pattern)
                context_start = max(0, start_pos - 20)
                context_end = min(len(content), start_pos + len(pattern) + 20)
                return f"...{content[context_start:context_end]}..."
                
        elif content_filter.filter_type == 'regex':
            # Para regex, tentar encontrar a correspondência
            import re
            flags = 0 if content_filter.case_sensitive else re.IGNORECASE
            match = re.search(content_filter.pattern, content, flags)
            if match:
                # Retornar o texto que correspondeu ao regex
                matched_text = match.group(0)
                start_pos = match.start()
                context_start = max(0, start_pos - 20)
                context_end = min(len(content), match.end() + 20)
                return f"...{content[context_start:context_end]}..."
        
        # Para outros tipos, retornar apenas uma amostra do conteúdo
        return content[:100] + '...' if len(content) > 100 else content
        
    except Exception as e:
        print(f"Erro ao extrair padrão: {e}")
        return content[:50] + '...' if len(content) > 50 else content