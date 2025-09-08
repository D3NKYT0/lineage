from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()

# Mapeamento de ícones por tipo de conteúdo (igual ao do admin)
CONTENT_TYPE_ICONS = {
    'index': 'fas fa-home',
    'about': 'fas fa-info-circle',
    'rules': 'fas fa-gavel',
    'commands': 'fas fa-terminal',
    'classes': 'fas fa-user-shield',
    'races': 'fas fa-users',
    'noblesse': 'fas fa-crown',
    'subclass': 'fas fa-layer-group',
    'hero': 'fas fa-star',
    'clan': 'fas fa-flag',
    'siege': 'fas fa-shield-alt',
    'olympiad': 'fas fa-trophy',
    'castle': 'fas fa-chess-rook',
    'fortress': 'fas fa-chess-king',
    'territory': 'fas fa-map-marked-alt',
    'events': 'fas fa-calendar-alt',
    'updates': 'fas fa-sync-alt',
    'features': 'fas fa-puzzle-piece',
    'rates': 'fas fa-percentage',
    'raids': 'fas fa-dragon',
    'assistance': 'fas fa-life-ring',
    'guide': 'fas fa-book-open',
    'faq': 'fas fa-question-circle',
    'other': 'fas fa-file-alt',
}

@register.simple_tag
def get_content_type_icon(content_type):
    """Retorna o ícone padrão para um tipo de conteúdo"""
    return CONTENT_TYPE_ICONS.get(content_type, 'fas fa-file-alt')

@register.simple_tag
def get_page_icon(page):
    """Retorna o ícone de uma página (personalizado ou padrão baseado no tipo)"""
    # Se o ícone personalizado existe e é FontAwesome, usa ele
    if page.icon and page.icon.startswith('fas '):
        return page.icon
    # Caso contrário, usa o ícone padrão baseado no tipo de conteúdo
    return CONTENT_TYPE_ICONS.get(page.content_type, 'fas fa-file-alt')
