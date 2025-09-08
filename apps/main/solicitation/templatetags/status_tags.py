from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def render_status(status, url_name, client_id):
    # Define as classes CSS e os ícones para cada status como tuplas
    status_classes = {
        'completo': ('text-success', 'fas fa-check-circle'),
        'incompleto': ('text-warning', 'fas fa-exclamation-circle'),
        'nao_realizado': ('text-danger', 'fas fa-times-circle'),
    }

    # Obtém as classes de estilo e ícone com base no status ou usa valores padrão
    css_class, icon_class = status_classes.get(status, ('text-danger', 'fas fa-times-circle'))

    # Gera a URL
    url = reverse(url_name, args=[client_id])

    # Determina o texto do status
    status_text = {
        'completo': 'Etapa Concluída',
        'incompleto': 'Etapa Incompleta',
        'nao_realizado': 'Etapa Não Realizada'
    }.get(status, 'Etapa Não Realizada')

    # Retorna o HTML marcado como seguro, aplicando a classe diretamente no <a>
    return mark_safe(f'''
        <a href="{url}" class="status-label {css_class}">
            <i class="{icon_class}"></i> {status_text}
        </a>
    ''')
