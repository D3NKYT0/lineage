import os
from django.conf import settings
from django.shortcuts import render

from core.context_processors import active_theme

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
            return render(request, f"installed/{theme_slug}/{template_name}", {**context, **context_processor_data})

    return render(request, f"{base_path}/{template_name}", context)
