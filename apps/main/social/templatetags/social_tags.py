from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
import re

register = template.Library()


@register.simple_tag
def verified_badge(user, size="16px", show_tooltip=True):
    """
    Exibe o símbolo de verificação para usuários verificados
    
    Args:
        user: Usuário a ser verificado
        size: Tamanho do ícone (ex: "16px", "20px")
        show_tooltip: Se deve mostrar tooltip explicativo
    """
    # Verificação mais robusta
    if not user:
        return ""
    
    # Verifica se o campo existe e é True
    try:
        # Acessar diretamente o campo do modelo
        is_verified = user.social_verified
        if not is_verified:
            return ""
    except Exception:
        # Se houver qualquer erro, não mostra o badge
        return ""
    
    tooltip_attr = f'title="{_("Conta verificada")}"' if show_tooltip else ""
    
    html = f'''
    <svg xmlns="http://www.w3.org/2000/svg" 
         viewBox="0 0 24 24" 
         style="width: {size}; height: {size}; display: inline-block; vertical-align: middle; margin-left: 2px;"
         {tooltip_attr}
         class="verified-badge">
        <circle cx="12" cy="12" r="10" fill="#1DA1F2"/>
        <path d="M9 12l2 2 4-4" stroke="white" stroke-width="2.5"/>
    </svg>
    '''
    
    return mark_safe(html)


@register.simple_tag
def user_display_name(user, show_verified=True, size="16px"):
    """
    Exibe o nome do usuário com símbolo de verificação se aplicável
    
    Args:
        user: Usuário a ser exibido
        show_verified: Se deve mostrar o símbolo de verificação
        size: Tamanho do ícone de verificação
    """
    if not user:
        return ""
    
    name = user.username
    verified_icon = verified_badge(user, size, show_tooltip=True) if show_verified else ""
    
    return mark_safe(f'{name}{verified_icon}')


@register.filter
def user_is_verified(user):
    """
    Filtro para verificar se um usuário é verificado na rede social
    """
    if not user:
        return False
    
    try:
        return user.social_verified
    except Exception:
        return False


@register.simple_tag
def profile_badge(user, size="16px", show_tooltip=True):
    """
    Exibe o badge do tipo de perfil do usuário
    
    Args:
        user: Usuário a ser verificado
        size: Tamanho do ícone (ex: "16px", "20px")
        show_tooltip: Se deve mostrar tooltip explicativo
    """
    if not user:
        return ""
    
    try:
        profile_type = user.profile_type
        if profile_type == 'regular':
            return ""
        
        display_name = user.profile_display_name
        icon_class = user.profile_icon
        color_class = user.profile_color_class
        
        tooltip_attr = f'title="{display_name}"' if show_tooltip else ""
        
        html = f'''
        <span class="profile-badge {color_class}" {tooltip_attr} style="display: inline-flex; align-items: center; margin-left: 4px;">
            <i class="bi {icon_class}" style="font-size: {size};"></i>
        </span>
        '''
        
        return mark_safe(html)
    except Exception:
        return ""


@register.simple_tag
def profile_type_display(user):
    """
    Exibe o nome do tipo de perfil do usuário
    """
    if not user:
        return ""
    
    try:
        return user.profile_display_name
    except Exception:
        return ""


@register.filter
def has_profile_type(user, profile_type):
    """
    Filtro para verificar se um usuário tem um tipo específico de perfil
    """
    if not user:
        return False
    
    try:
        return user.profile_type == profile_type
    except Exception:
        return False


@register.filter
def mention_links(text):
    """
    Converte menções @username em links clicáveis para o perfil do usuário
    
    Args:
        text: Texto que pode conter menções @username
        
    Returns:
        Texto com menções convertidas em links HTML
    """
    if not text:
        return text
    
    # Converter para string se não for
    text = str(text)
    
    # Padrão para encontrar menções @username
    # Aceita letras, números, underscores e hífens no username
    # Não deve começar com @ se já estiver dentro de uma menção
    mention_pattern = r'(?<!@)@([a-zA-Z0-9_-]+)'
    
    def replace_mention(match):
        username = match.group(1)
        
        # Ignorar se o username for muito longo (provavelmente não é uma menção válida)
        if len(username) > 30:
            return match.group(0)
        
        try:
            # Verificar se o usuário existe
            User = get_user_model()
            user = User.objects.filter(username=username).first()
            
            if user:
                # Usuário existe, criar link
                profile_url = reverse('social:user_profile', kwargs={'username': username})
                return f'<a href="{profile_url}" class="mention-link" data-username="{username}">@{username}</a>'
            else:
                # Usuário não existe, manter como texto simples
                return f'<span class="mention-invalid">@{username}</span>'
                
        except Exception:
            # Em caso de erro, manter como texto simples
            return f'<span class="mention-invalid">@{username}</span>'
    
    # Aplicar a substituição
    try:
        processed_text = re.sub(mention_pattern, replace_mention, text)
    except Exception:
        # Em caso de erro na regex, manter texto original
        processed_text = text
    
    return mark_safe(processed_text)


@register.filter
def process_content(text):
    """
    Processa o conteúdo do post convertendo URLs e hashtags em links clicáveis
    
    Args:
        text: Texto que pode conter URLs, hashtags e menções
        
    Returns:
        Texto com URLs, hashtags e menções convertidas em links HTML
    """
    if not text:
        return text
    
    # Converter para string se não for
    text = str(text)
    
    # Proteção contra textos muito longos que podem causar travamento
    if len(text) > 10000:
        return mark_safe(text)
    
    # Função para verificar se uma posição está dentro de uma tag HTML
    def is_inside_html_tag(text, pos):
        """Verifica se a posição está dentro de uma tag HTML"""
        # Procurar para trás pela tag de abertura mais próxima
        i = pos - 1
        while i >= 0:
            if text[i] == '>':
                return False  # Encontrou fechamento de tag antes da abertura
            elif text[i] == '<':
                # Verificar se é uma tag de abertura
                j = i + 1
                while j < len(text) and text[j].isalnum():
                    j += 1
                if j < len(text) and text[j] == '>':
                    return True  # Está dentro de uma tag HTML
                return False
            i -= 1
        return False
    
    # 1. Processar URLs primeiro (para evitar conflitos com hashtags)
    # Padrão para URLs (http/https) - versão mais robusta
    url_pattern = r'(https?://[^\s<>"{}|\\^`\[\]]{1,2000})'
    
    def replace_url(match):
        url = match.group(1)
        # Validar URL básica
        if not url or len(url) < 10 or len(url) > 2000:
            return match.group(0)
        
        # Truncar URL para exibição se for muito longa
        display_url = url
        if len(url) > 50:
            display_url = url[:47] + '...'
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer" class="content-link">{display_url}</a>'
    
    # Aplicar substituição de URLs com limite de tentativas
    try:
        processed_text = re.sub(url_pattern, replace_url, text, flags=re.IGNORECASE)
    except Exception:
        # Em caso de erro na regex, manter texto original
        processed_text = text
    
    # 2. Processar hashtags
    hashtag_pattern = r'#([a-zA-Z0-9_]+)'
    
    def replace_hashtag(match):
        hashtag_name = match.group(1)
        start_pos = match.start()
        
        # Verificar se está dentro de uma tag HTML
        if is_inside_html_tag(processed_text, start_pos):
            return match.group(0)  # Manter como está
        
        # Ignorar hashtags muito longas
        if len(hashtag_name) > 30:
            return match.group(0)
        
        try:
            # Criar link para a hashtag
            hashtag_url = reverse('social:hashtag_detail', kwargs={'hashtag_name': hashtag_name.lower()})
            return f'<a href="{hashtag_url}" class="hashtag-link">#{hashtag_name}</a>'
        except Exception:
            # Em caso de erro, manter como texto simples
            return f'<span class="hashtag-invalid">#{hashtag_name}</span>'
    
    # Aplicar substituição de hashtags
    try:
        processed_text = re.sub(hashtag_pattern, replace_hashtag, processed_text)
    except Exception:
        # Em caso de erro na regex, manter texto atual
        pass
    
    # 3. Processar menções @username
    mention_pattern = r'@([a-zA-Z0-9_-]+)'
    
    def replace_mention(match):
        username = match.group(1)
        start_pos = match.start()
        
        # Verificar se está dentro de uma tag HTML
        if is_inside_html_tag(processed_text, start_pos):
            return match.group(0)  # Manter como está
        
        # Ignorar se o username for muito longo
        if len(username) > 30:
            return match.group(0)
        
        try:
            # Verificar se o usuário existe
            User = get_user_model()
            user = User.objects.filter(username=username).first()
            
            if user:
                # Usuário existe, criar link
                profile_url = reverse('social:user_profile', kwargs={'username': username})
                return f'<a href="{profile_url}" class="mention-link" data-username="{username}">@{username}</a>'
            else:
                # Usuário não existe, manter como texto simples
                return f'<span class="mention-invalid">@{username}</span>'
                
        except Exception:
            # Em caso de erro, manter como texto simples
            return f'<span class="mention-invalid">@{username}</span>'
    
    # Aplicar substituição de menções
    try:
        processed_text = re.sub(mention_pattern, replace_mention, processed_text)
    except Exception:
        # Em caso de erro na regex, manter texto atual
        pass
    
    return mark_safe(processed_text)
