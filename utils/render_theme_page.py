import os
import logging
from django.conf import settings
from django.shortcuts import render
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.urls.exceptions import NoReverseMatch
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import Context

from core.context_processors import active_theme

# Configure logger
logger = logging.getLogger(__name__)

def render_theme_page(request, base_path, template_name, context=None):
    """
    Função para renderizar a página do tema, verificando se o arquivo existe no tema ativo.
    Se o arquivo não existir, será utilizado o fallback.
    """
    if context is None:
        context = {}

    # Obtem contexto adicional do context processor
    context_processor_data = active_theme(request)

    theme_slug = context_processor_data.get('theme_slug', '')

    if theme_slug:
        theme_path = os.path.join(settings.BASE_DIR, 'themes', 'installed', theme_slug)
        theme_file_path = os.path.join(theme_path, template_name)

        if os.path.isfile(theme_file_path):
            try:
                return render(request, f"installed/{theme_slug}/{template_name}", {**context, **context_processor_data})
            except (TemplateDoesNotExist, TemplateSyntaxError) as e:
                # Erro de template (arquivo não encontrado ou sintaxe inválida)
                logger.error(f"Template error in theme '{theme_slug}': {str(e)}")
                
                if getattr(settings, 'SHOW_THEME_ERRORS_TO_USERS', True):
                    error_context = {
                        'error_type': 'template_error',
                        'error_message': f'O tema "{theme_slug}" possui um template com erro: {str(e)}',
                        'theme_slug': theme_slug,
                        'template_name': template_name,
                        'fallback_message': 'Utilizando template padrão como alternativa.',
                        **context
                    }
                else:
                    error_context = context
                
                return render(request, f"{base_path}/{template_name}", error_context)
            except NoReverseMatch as e:
                # Erro de URL inválida no template
                logger.error(f"URL error in theme '{theme_slug}': {str(e)}")
                
                if getattr(settings, 'SHOW_THEME_ERRORS_TO_USERS', True):
                    error_context = {
                        'error_type': 'url_error',
                        'error_message': f'O tema "{theme_slug}" contém URLs inválidas: {str(e)}',
                        'theme_slug': theme_slug,
                        'template_name': template_name,
                        'fallback_message': 'Utilizando template padrão como alternativa. Entre em contato com o administrador para corrigir as URLs do tema.',
                        'url_error_details': str(e),
                        **context
                    }
                else:
                    error_context = context
                
                return render(request, f"{base_path}/{template_name}", error_context)
            except Exception as e:
                # Outros erros de renderização
                logger.error(f"Render error in theme '{theme_slug}': {str(e)}")
                
                if getattr(settings, 'SHOW_THEME_ERRORS_TO_USERS', True):
                    error_context = {
                        'error_type': 'render_error',
                        'error_message': f'Erro ao renderizar o tema "{theme_slug}": {str(e)}',
                        'theme_slug': theme_slug,
                        'template_name': template_name,
                        'fallback_message': 'Utilizando template padrão como alternativa.',
                        **context
                    }
                else:
                    error_context = context
                
                return render(request, f"{base_path}/{template_name}", error_context)

    return render(request, f"{base_path}/{template_name}", context)
