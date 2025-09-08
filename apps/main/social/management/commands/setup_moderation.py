from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from apps.main.social.models import ContentFilter


class Command(BaseCommand):
    help = 'Configura filtros otimizados de moderação específicos e eficazes'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Configurando filtros otimizados de moderação...')
        )

        # ============================================================================
        # FILTROS DE SPAM E MARKETING - OTIMIZADOS
        # ============================================================================
        spam_filters = [
            {
                'name': 'Spam - Ofertas Comerciais Agressivas',
                'filter_type': 'regex',
                'pattern': r'\b(ganhe|ganhar|dinheiro|fácil|rápido|grátis|urgente|agora|clique|click)\b.*\b(ganhe|ganhar|dinheiro|fácil|rápido|grátis|urgente|agora|clique|click)\b',
                'action': 'flag',
                'description': 'Detecta spam comercial com múltiplas palavras-chave agressivas',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Spam - Medicamentos e Suplementos',
                'filter_type': 'regex',
                'pattern': r'\b(viagra|cialis|levitra|pharmacy|medicine|pills|prescription|weight\s*loss|diet|supplement|testosterone)\b',
                'action': 'auto_hide',
                'description': 'Detecta spam de medicamentos e suplementos com precisão',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Spam - Esquemas Financeiros Suspeitos',
                'filter_type': 'regex',
                'pattern': r'\b(pyramid\s*scheme|ponzi|investment|bitcoin|crypto|trading|forex|binary\s*options|get\s*rich\s*quick|passive\s*income)\b',
                'action': 'flag',
                'description': 'Detecta esquemas financeiros suspeitos e golpes',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # ============================================================================
        # FILTROS DE LINGUAGEM INADEQUADA - ESPECÍFICOS
        # ============================================================================
        profanity_filters = [
            {
                'name': 'Palavrões - Português (Leve)',
                'filter_type': 'regex',
                'pattern': r'\b(porra|merda|caralho|cacete)\b',
                'action': 'flag',
                'description': 'Detecta palavrões leves em português',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': True
            },
            {
                'name': 'Palavrões - Português (Severo)',
                'filter_type': 'regex',
                'pattern': r'\b(viado|bicha|gay\s*de\s*merda|cu|cuzão|arrombado|filho\s*da\s*puta|fdp)\b',
                'action': 'auto_hide',
                'description': 'Detecta palavrões ofensivos e discriminatórios',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': True
            },
            {
                'name': 'Palavrões com Símbolos',
                'filter_type': 'regex',
                'pattern': r'\b(p\*rra|m\*rda|c\*ralho|p\*ta|f\*ck|sh\*t|b\*tch|a\*shole)\b',
                'action': 'flag',
                'description': 'Detecta palavrões com asteriscos ou símbolos',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': True
            }
        ]

        # ============================================================================
        # FILTROS CONTRA PORNOGRAFIA - PRECISOS
        # ============================================================================
        adult_content_filters = [
            {
                'name': 'Conteúdo Pornográfico Explícito',
                'filter_type': 'regex',
                'pattern': r'\b(porn|porno|pornografia|sex|sexo|nude|nudes|naked|pelada|gostosa|bunduda|peituda)\b',
                'action': 'auto_hide',
                'description': 'Detecta conteúdo pornográfico explícito',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': True
            },
            {
                'name': 'Sites Pornográficos',
                'filter_type': 'regex',
                'pattern': r'(pornhub|xvideos|redtube|youporn|xhamster|xnxx|brazzers|onlyfans)',
                'action': 'auto_delete',
                'description': 'Detecta links para sites pornográficos conhecidos',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # ============================================================================
        # FILTROS DE URLS SUSPEITAS - MELHORADOS
        # ============================================================================
        suspicious_urls_filters = [
            {
                'name': 'Encurtadores de URL Suspeitos',
                'filter_type': 'regex',
                'pattern': r'http[s]?://(bit\.ly|tinyurl|goo\.gl|t\.co|short\.link|tiny\.cc|ow\.ly|is\.gd)',
                'action': 'flag',
                'description': 'Detecta URLs de encurtadores que podem ocultar conteúdo malicioso',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Domínios Suspeitos de Phishing',
                'filter_type': 'regex',
                'pattern': r'(\.tk|\.ml|\.ga|\.cf|tempmail|guerrillamail|10minutemail)',
                'action': 'auto_hide',
                'description': 'Detecta domínios suspeitos frequentemente usados para phishing',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Múltiplas URLs (Spam)',
                'filter_type': 'regex',
                'pattern': r'http[s]?://[^\s]+.*http[s]?://[^\s]+.*http[s]?://[^\s]+',
                'action': 'flag',
                'description': 'Detecta posts com muitas URLs (possível spam)',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # ============================================================================
        # FILTROS CONTRA DISCRIMINAÇÃO - ESPECÍFICOS
        # ============================================================================
        hate_speech_filters = [
            {
                'name': 'Discurso de Ódio Racial',
                'filter_type': 'regex',
                'pattern': r'\b(nigger|negro\s*de\s*merda|macaco|preto\s*fedorento)\b',
                'action': 'auto_delete',
                'description': 'Detecta linguagem racista e discriminatória',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': True
            },
            {
                'name': 'Discurso de Ódio Homofóbico',
                'filter_type': 'regex',
                'pattern': r'\b(viado\s*nojento|gay\s*de\s*merda|sapatão|traveco)\b',
                'action': 'auto_delete',
                'description': 'Detecta linguagem homofóbica e transfóbica',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': True
            }
        ]

        # ============================================================================
        # FILTROS CONTRA DESINFORMAÇÃO - PRECISOS
        # ============================================================================
        misinformation_filters = [
            {
                'name': 'Fake News Médicas',
                'filter_type': 'regex',
                'pattern': r'\b(vacina\s*mata|autismo|cura\s*cancer|milagre|remedio\s*caseiro|covid\s*fake)\b',
                'action': 'flag',
                'description': 'Detecta possível desinformação médica',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # ============================================================================
        # FILTROS DE COMPORTAMENTO - INTELIGENTES
        # ============================================================================
        behavior_filters = [
            {
                'name': 'Conteúdo Repetitivo (Spam)',
                'filter_type': 'regex',
                'pattern': r'(.{10,})\1{3,}',
                'action': 'flag',
                'description': 'Detecta conteúdo repetitivo (possível spam)',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'CAPS Excessivo',
                'filter_type': 'regex',
                'pattern': r'[A-Z]{20,}',
                'action': 'flag',
                'description': 'Detecta texto em maiúsculas excessivo',
                'case_sensitive': True,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Informações Pessoais',
                'filter_type': 'regex',
                'pattern': r'(\d{3}[-.]?\d{3}[-.]?\d{3}[-.]?\d{2}|\(\d{2}\)\s?\d{4,5}[-.]?\d{4}|whatsapp|telefone|celular)',
                'action': 'flag',
                'description': 'Detecta possível compartilhamento de informações pessoais',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # ============================================================================
        # FILTROS ESPECÍFICOS PARA BRASIL - OTIMIZADOS
        # ============================================================================
        brazil_specific_filters = [
            {
                'name': 'Golpes Brasileiros - PIX',
                'filter_type': 'regex',
                'pattern': r'\b(pix\s*gratis|auxilio\s*emergencial|bolsa\s*familia|cpf\s*liberado|fgts\s*saque)\b',
                'action': 'flag',
                'description': 'Detecta golpes comuns no Brasil relacionados a PIX e benefícios',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Sites de Apostas Brasileiros',
                'filter_type': 'regex',
                'pattern': r'\b(blaze|crash|mines|aviator|fortune\s*tiger|jogo\s*do\s*bicho|bets)\b',
                'action': 'flag',
                'description': 'Detecta referências a sites de apostas populares no Brasil',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # Combinar todos os filtros otimizados
        all_filters = (spam_filters + profanity_filters + adult_content_filters + 
                      suspicious_urls_filters + hate_speech_filters + misinformation_filters + 
                      behavior_filters + brazil_specific_filters)

        created_count = 0
        updated_count = 0

        for filter_data in all_filters:
            filter_obj, created = ContentFilter.objects.get_or_create(
                name=filter_data['name'],
                defaults=filter_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Criado filtro: {filter_data["name"]}')
                )
            else:
                # Atualizar filtro existente
                for key, value in filter_data.items():
                    setattr(filter_obj, key, value)
                filter_obj.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Atualizado filtro: {filter_data["name"]}')
                )

        # Criar filtro de padrão de spam automático
        spam_pattern_filter, created = ContentFilter.objects.get_or_create(
            name='Padrão de Spam Automático',
            defaults={
                'filter_type': 'spam_pattern',
                'pattern': 'auto',
                'action': 'flag',
                'description': 'Detecta automaticamente padrões comuns de spam usando algoritmos internos',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        )

        if created:
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS('✓ Criado filtro de padrão de spam automático')
            )

        # Mensagem final com estatísticas
        total_active = ContentFilter.objects.filter(is_active=True).count()
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*60}\n'
                f'🛡️  SISTEMA DE MODERAÇÃO OTIMIZADO!\n'
                f'{"="*60}\n'
                f'📊 Estatísticas:\n'
                f'   • Filtros criados: {created_count}\n'
                f'   • Filtros atualizados: {updated_count}\n'
                f'   • Total de filtros ativos: {total_active}\n\n'
                f'🎯 Categorias otimizadas:\n'
                f'   • Spam e Marketing (3 filtros precisos)\n'
                f'   • Palavrões (3 níveis de severidade)\n'
                f'   • Conteúdo Pornográfico (2 filtros específicos)\n'
                f'   • URLs Suspeitas (3 filtros inteligentes)\n'
                f'   • Discurso de Ódio (2 filtros específicos)\n'
                f'   • Fake News (1 filtro médico)\n'
                f'   • Comportamentos Suspeitos (3 filtros inteligentes)\n'
                f'   • Golpes Brasileiros (2 filtros específicos)\n\n'
                f'✨ Melhorias implementadas:\n'
                f'   • Filtros mais específicos e precisos\n'
                f'   • Regex otimizadas para melhor performance\n'
                f'   • Remoção de filtros genéricos e inúteis\n'
                f'   • Foco em padrões reais de spam e abuso\n'
                f'   • Ações apropriadas para cada tipo de conteúdo\n\n'
                f'🔧 Próximos passos:\n'
                f'   1. Monitore a eficácia dos filtros\n'
                f'   2. Ajuste ações conforme necessário\n'
                f'   3. Adicione filtros específicos se necessário\n\n'
                f'📋 Acesse: /admin/social/contentfilter/ para gerenciar\n'
                f'{"="*60}'
            )
        )
